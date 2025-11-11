# src/indexer.py
import os, json
from src.config import DATA_DIR, DOCS_JSON, MAX_NEW_DOCS_PER_RUN, DISABLE_EMBEDDINGS

os.makedirs(DATA_DIR, exist_ok=True)

def persist_docs(docs):
    with open(DOCS_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

def load_docs():
    if not os.path.exists(DOCS_JSON): return []
    with open(DOCS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def add_articles_to_corpus(entries):
    """
    Lite: store title/link/summary as 'text'. No chunking/embeddings.
    Each doc: {id,title,link,published,text}
    """
    docs = load_docs()
    known = {d["link"] for d in docs}
    new = []
    for e in entries:
        if len(new) >= MAX_NEW_DOCS_PER_RUN: break
        link = e.get("link") or ""
        if not link or link in known: continue
        text = (e.get("summary") or "").strip()
        if not text: continue
        doc = {
            "id": str(len(docs)+len(new)),
            "title": e.get("title","") or "(untitled)",
            "link": link,
            "published": e.get("published", 0),
            "text": text[:8000],
        }
        new.append(doc)
    if new:
        docs.extend(new)
        persist_docs(docs)
    return docs, new

# The following are stubs in Lite mode
def rebuild_vectorstore_from_docs(docs):
    # No embeddings in Lite → return number of docs as a proxy
    return len(docs)

def search(query, top_k=5):
    # Lite mode disables semantic search
    return [] if DISABLE_EMBEDDINGS else []
