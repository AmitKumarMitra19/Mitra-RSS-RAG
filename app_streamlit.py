# app_streamlit.py
import os, sys, traceback
import streamlit as st

from src.config import (
    FEEDS, TOP_K, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    MAX_FEEDS, PER_FEED_LIMIT, OVERALL_ENTRY_LIMIT,
    MAX_NEW_DOCS_PER_RUN, MAX_SUMMARY_ITEMS_IN_DIGEST,
    USE_RSS_SUMMARY_ONLY
)
from src.loader import fetch_rss_entries, fetch_article_text
from src.indexer import load_docs, add_articles_to_corpus, rebuild_vectorstore_from_docs, search
from src.summarize import summarize_article
from src.push import send_telegram_message

st.set_page_config(page_title="RSS RAG → Telegram", page_icon="📰")
st.title("📰 RSS RAG → Telegram")

with st.expander("🔧 Diagnostics"):
    st.write("Python:", sys.version)
    st.write("Feeds configured:", FEEDS)
    st.write("Limits:", {
        "MAX_FEEDS": MAX_FEEDS,
        "PER_FEED_LIMIT": PER_FEED_LIMIT,
        "OVERALL_ENTRY_LIMIT": OVERALL_ENTRY_LIMIT,
        "MAX_NEW_DOCS_PER_RUN": MAX_NEW_DOCS_PER_RUN,
        "MAX_SUMMARY_ITEMS_IN_DIGEST": MAX_SUMMARY_ITEMS_IN_DIGEST,
        "USE_RSS_SUMMARY_ONLY": USE_RSS_SUMMARY_ONLY,
    })
    st.write("Has TELEGRAM_BOT_TOKEN:", bool(TELEGRAM_BOT_TOKEN))
    st.write("TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else "(missing)")
    if st.button("Send test message"):
        try:
            send_telegram_message("✅ Streamlit secrets wired correctly.")
            st.success("Test message sent.")
        except Exception as e:
            st.error("Failed:")
            st.exception(e)

with st.expander("📜 Feeds in use"):
    st.write(FEEDS)

# ------------- NEW: Debug-only fetch button (no indexing, no embedding) -------------
if st.button("🧪 Fetch (Debug only)"):
    try:
        with st.spinner("Fetching limited entries for debug…"):
            entries = fetch_rss_entries(FEEDS)
        st.success(f"Fetched {len(entries)} entries (capped). Showing first 6:")
        for e in entries[:6]:
            st.write("•", e.get("title"), "→", e.get("link"))
        st.info("If this works, fetching is not the crash point.")
    except Exception as e:
        st.error("Fetch crashed with exception below:")
        st.exception(e)

st.write("---")

col1, col2 = st.columns(2)

def _hydrate(entries):
    """Attach full_text unless summary-only mode is enabled."""
    if USE_RSS_SUMMARY_ONLY:
        for e in entries: e["full_text"] = ""  # force summary fallback
        return entries
    non_empty = 0
    for i, e in enumerate(entries, 1):
        try:
            e["full_text"] = fetch_article_text(e["link"])
            if e["full_text"]: non_empty += 1
        except Exception:
            e["full_text"] = ""
    st.info(f"Extraction done. Entries: {len(entries)} | Non-empty full_text: {non_empty}")
    return entries

with col1:
    if st.button("🔄 Fetch & Index Now"):
        try:
            with st.spinner("Fetching limited set of entries…"):
                entries = fetch_rss_entries(FEEDS)
                st.info(f"Fetched {len(entries)} entries (capped).")
            with st.spinner("Hydrating (summary-only mode if enabled)…"):
                entries = _hydrate(entries)
            with st.spinner("Adding new docs and rebuilding index…"):
                docs, new_docs = add_articles_to_corpus(entries)
                chunks = rebuild_vectorstore_from_docs(docs)
            st.success(f"Indexed {len(new_docs)} new article(s). Total chunks: {chunks}")
        except Exception as e:
            st.error("Indexing failed. See details below:")
            st.exception(e)

with col2:
    if st.button("📨 Send Latest Digest to Telegram"):
        try:
            with st.spinner("Fetching & building digest…"):
                entries = fetch_rss_entries(FEEDS)
                entries = _hydrate(entries)
                docs, new_docs = add_articles_to_corpus(entries)
                if new_docs:
                    items = new_docs[:MAX_SUMMARY_ITEMS_IN_DIGEST]
                    parts = []
                    for d in items:
                        try:
                            s = summarize_article(d["title"], d["text"])
                        except Exception:
                            s = (d["text"][:600] + "…") if d["text"] else "(no summary)"
                        parts.append(f"• <b>{d['title']}</b>\n{s}\n\n🔗 {d['link']}")
                    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
                    send_telegram_message(digest[:3900])
                    st.success(f"Digest sent. Items: {len(items)}")
                else:
                    st.info("No new articles.")
        except Exception as e:
            st.error("Sending digest failed. See details below:")
            st.exception(e)

st.write("---")
st.subheader("🔎 Ask the RAG")
q = st.text_input("Your question")
topk = st.slider("Top-K", 1, 10, TOP_K)

if st.button("Search") and q.strip():
    try:
        with st.spinner("Searching…"):
            hits = search(q, top_k=topk)
        if not hits:
            st.warning("Index empty or no results. Click '🔄 Fetch & Index Now' first.")
        else:
            for h in hits:
                st.markdown(f"**[{h['rank']}] {h['title']}**  \nScore: `{h['score']:.3f}`  \n[{h['link']}]({h['link']})")
                st.write(h["chunk"][:800] + "…")
                st.write("---")
    except Exception as e:
        st.error("Search failed.")
        st.exception(e)
