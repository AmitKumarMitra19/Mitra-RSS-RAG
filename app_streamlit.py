import os, sys, traceback
import streamlit as st

from src.config import (
    FEEDS, TOP_K, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    MAX_FEED_ENTRIES_PER_RUN, MAX_NEW_DOCS_PER_RUN, MAX_SUMMARY_ITEMS_IN_DIGEST
)
from src.loader import fetch_rss_entries, fetch_article_text
from src.indexer import load_docs, add_articles_to_corpus, rebuild_vectorstore_from_docs, search
from src.summarize import summarize_article
from src.push import send_telegram_message

st.set_page_config(page_title="RSS RAG → Telegram", page_icon="📰")
st.title("📰 RSS RAG → Telegram")

with st.expander("🔧 Diagnostics"):
    st.write("Python:", sys.version)
    st.write("Feeds:", FEEDS)
    st.write("Top-K:", TOP_K)
    st.write("Limits:", {
        "MAX_FEED_ENTRIES_PER_RUN": MAX_FEED_ENTRIES_PER_RUN,
        "MAX_NEW_DOCS_PER_RUN": MAX_NEW_DOCS_PER_RUN,
        "MAX_SUMMARY_ITEMS_IN_DIGEST": MAX_SUMMARY_ITEMS_IN_DIGEST
    })
    st.write("Has token:", bool(TELEGRAM_BOT_TOKEN))
    st.write("Chat ID:", TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else "(missing)")
    if st.button("Send test message"):
        try:
            send_telegram_message("✅ Streamlit secrets wired correctly.")
            st.success("Test message sent.")
        except Exception as e:
            st.error("Failed:")
            st.exception(e)

with st.expander("📜 Feeds in use"):
    st.write(FEEDS)

col1, col2 = st.columns(2)

def _process_entries_for_index(entries):
    # CAP how many entries we try this run
    entries = entries[:MAX_FEED_ENTRIES_PER_RUN]
    texts_ok = 0
    for i, e in enumerate(entries, 1):
        try:
            e["full_text"] = fetch_article_text(e["link"])
            if e["full_text"]:
                texts_ok += 1
        except Exception:
            e["full_text"] = ""
        if i % 10 == 0:
            st.info(f"Processed {i}/{len(entries)} entries… (non-empty texts: {texts_ok})")
    return entries

with col1:
    if st.button("🔄 Fetch & Index Now"):
        try:
            with st.spinner("Fetching feeds…"):
                entries = fetch_rss_entries(FEEDS)
                st.info(f"Fetched {len(entries)} entries.")
            with st.spinner("Extracting article text (with fallbacks)…"):
                entries = _process_entries_for_index(entries)
            with st.spinner(f"Adding up to {MAX_NEW_DOCS_PER_RUN} new docs + rebuilding index…"):
                docs, new_docs = add_articles_to_corpus(entries)
                chunks = rebuild_vectorstore_from_docs(docs)
            st.success(f"Indexed {len(new_docs)} new article(s). Total chunks: {chunks}")
        except Exception as e:
            st.error("Indexing failed.")
            st.exception(e)

with col2:
    if st.button("📨 Send Latest Digest to Telegram"):
        try:
            with st.spinner("Fetching latest & building digest…"):
                entries = fetch_rss_entries(FEEDS)
                entries = _process_entries_for_index(entries)
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
                    st.success(f"Digest sent to Telegram. Items: {len(items)}")
                else:
                    st.info("No new articles.")
        except Exception as e:
            st.error("Sending digest failed.")
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
