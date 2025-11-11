import os, json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.config import (
    DATA_DIR, INDEX_DIR, DOCS_JSON, FAISS_PATH, EMB_NPY, EMB_MODEL,
    MAX_NEW_DOCS_PER_RUN, MAX_CHUNKS_FOR_EMBED
)

# Optional Streamlit cache (no-op outside Streamlit)
try:
    import streamlit as st
    cache_resource = st.cache_resource
    cache_data = st.cache_data
except Exception:
    def cache_resource(f): return f
    def cache_data(f): return f

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

@cache_resource
def get_embedder():
    # Use CPU in Cloud
    return SentenceTransformer(EMB_MODEL, device="cpu")

def build_embeddings(texts, batch_size=64):
    model = get_embedder()
    # CAP total chunks to avoid OOM
    texts = texts[:MAX_CHUNKS_FOR_EMBED]
    embs = model.encode(
        texts, batch_size=batch_size, convert_to_numpy=True, normalize_embeddings=True
    )
    return embs

def save_index(embeddings: np.ndarray):
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype("float32"))
    faiss.write_index(index, FAISS_PATH)
    np.save(EMB_NPY, embeddings)

def load_index():
    if not os.path.exists(FAISS_PATH):
        return None
    index = faiss.read_index(FAISS_PATH)
    embs = np.load(EMB_NPY)
    return index, embs

def persist_docs(docs):
    with open(DOCS_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

def load_docs():
    if not os.path.exists(DOCS_JSON):
        return []
    with open(DOCS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def chunk_text(text, chunk_size=800, overlap=120):
    words = text.split()
    if not words:
        return []
    chunks, i = [], 0
    while i < len(words):
        j = min(len(words), i + chunk_size)
        chunks.append(" ".join(words[i:j]))
        i = max(0, j - overlap)
    return chunks

def add_articles_to_corpus(entries):
    """
    FALLBACK: if 'full_text' empty, use RSS 'summary' so we always index something.
    Apply MAX_NEW_DOCS_PER_RUN cap to avoid huge batches on Cloud.
    """
    docs = load_docs()
    known_links = {d["link"] for d in docs}
    new = []

    for e in entries:
        if len(new) >= MAX_NEW_DOCS_PER_RUN:
            break
        link = e.get("link") or ""
        if not link or link in known_links:
            continue

        text = (e.get("full_text") or "").strip()
        if not text:
            text = (e.get("summary") or "").strip()
        if not text:
            continue

        chunks = chunk_text(text)
        if not chunks:
            continue

        doc = {
            "id": str(len(docs) + len(new)),
            "title": e.get("title", "") or "(untitled)",
            "link": link,
            "published": e.get("published", 0),
            "text": text[:20000],  # hard cap per-doc text
            "chunks": chunks,
        }
        new.append(doc)

    if new:
        docs.extend(new)
        persist_docs(docs)
    return docs, new

def rebuild_vectorstore_from_docs(docs):
    texts = [c for d in docs for c in d["chunks"]]
    if not texts:
        return 0
    embs = build_embeddings(texts)
    save_index(embs)
    return len(texts)

def search(query, top_k=5):
    from src.config import TOP_K
    top_k = top_k or TOP_K
    pack = load_index()
    if pack is None:
        return []
    index, _ = pack
    model = get_embedder()
    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, idxs = index.search(q.astype("float32"), top_k)

    docs = load_docs()
    pairs = []
    for di, d in enumerate(docs):
        for ci in range(len(d["chunks"])):
            pairs.append((di, ci))

    results = []
    for rank, idx in enumerate(idxs[0]):
        if idx < 0 or idx >= len(pairs):
            continue
        di, ci = pairs[idx]
        d = docs[di]
        results.append({
            "rank": rank + 1,
            "score": float(scores[0][rank]),
            "title": d["title"],
            "link": d["link"],
            "chunk": d["chunks"][ci],
            "doc_id": d["id"],
        })
    return results
