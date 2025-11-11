# app_streamlit.py
import os, sys
import streamlit as st
from src.config import (
    FEEDS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    MAX_FEEDS, PER_FEED_LIMIT, OVERALL_ENTRY_LIMIT,
    MAX_NEW_DOCS_PER_RUN, MAX_SUMMARY_ITEMS_IN_DIGEST,
    USE_RSS_SUMMARY_ONLY, DISABLE_SUMMARIZER, DISABLE_EMBEDDINGS
)
from src.loader import fetch_rss_entries
from src.indexer import load_docs, add_articles_to_corpus, rebuild_vectorstore_from_docs
from src.summarize import summarize_article
from src.push import send_telegram_message

st.set_page_config(page_title="RSS RAG → Telegram (Lite)", page_icon="📰")
st.title("📰 RSS RAG → Telegram — Lite mode")

with st.expander("🔧 Diagnostics"):
    st.write("Python:", sys.version)
    st.write("Feeds:", FEEDS)
    st.write("Limits:", {
        "MAX_FEEDS": MAX_FEEDS,
        "PER_FEED_LIMIT": PER_FEED_LIMIT,
        "OVERALL_ENTRY_LIMIT": OVERALL_ENTRY_LIMIT,
        "MAX_NEW_DOCS_PER_RUN": MAX_NEW_DOCS_PER_RUN,
        "MAX_SUMMARY_ITEMS_IN_DIGEST": MAX_SUMMARY_ITEMS_IN_DIGEST
    })
    st.write("Lite switches:", {
        "USE_RSS_SUMMARY_ONLY": USE_RSS_SUMMARY_ONLY,
        "DISABLE_SUMMARIZER": DISABLE_SUMMARIZER,
        "DISABLE_EMBEDDINGS": DISABLE_EMBEDDINGS
    })
    st.write("Has TELEGRAM_BOT_TOKEN:", bool(TELEGRAM_BOT_TOKEN))
    st.write("TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else "(missing)")
    if st.button("Send test message"):
        try:
            send_telegram_message("✅ Telegram wired correctly (Lite mode).")
            st.success("Test message sent.")
        except Exception as e:
            st.error(f"Failed: {e}")

with st.expander("📜 Feeds in use"):
    st.write(FEEDS)

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Fetch & Store (Lite)"):
        try:
            with st.spinner("Fetching limited RSS summaries…"):
                entries = fetch_rss_entries(FEEDS)
                st.info(f"Fetched {len(entries)} entries (capped).")
            with st.spinner("Storing new docs (no embeddings)…"):
                docs, new_docs = add_articles_to_corpus(entries)
                count_proxy = rebuild_vectorstore_from_docs(docs)  # returns len(docs)
            st.success(f"Stored {len(new_docs)} new article(s). Total stored: {count_proxy}")
        except Exception as e:
            st.error("Fetch/Store failed.")
            st.exception(e)

with col2:
    if st.button("📨 Send Digest (Lite)"):
        try:
            with st.spinner("Fetching & building digest from summaries…"):
                entries = fetch_rss_entries(FEEDS)
                docs, new_docs = add_articles_to_corpus(entries)
                if new_docs:
                    items = new_docs[:MAX_SUMMARY_ITEMS_IN_DIGEST]
                    parts = []
                    for d in items:
                        s = summarize_article(d["title"], d["text"])
                        parts.append(f"• <b>{d['title']}</b>\n{s}\n\n🔗 {d['link']}")
                    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
                    send_telegram_message(digest[:3900])
                    st.success(f"Digest sent. Items: {len(items)}")
                else:
                    st.info("No new articles.")
        except Exception as e:
            st.error("Digest failed.")
            st.exception(e)

st.write("---")
st.caption("Lite mode: no page fetching, no transformers, no embeddings. Stable & cheap.")
