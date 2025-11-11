import os, sys
import streamlit as st
from src.config import FEEDS, TOP_K, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
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
    st.write("Has token:", bool(TELEGRAM_BOT_TOKEN))
    st.write("Chat ID:", TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else "(missing)")
    if st.button("Send test message"):
        try:
            send_telegram_message("✅ Streamlit secrets wired correctly.")
            st.success("Test message sent.")
        except Exception as e:
            st.error(f"Failed: {e}")

with st.expander("📜 Feeds in use"):
    st.write(FEEDS)

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Fetch & Index Now"):
        try:
            with st.spinner("Fetching & indexing…"):
                entries = fetch_rss_entries(FEEDS)
                st.info(f"Fetched {len(entries)} entries from RSS.")
                for e in entries:
                    e["full_text"] = fetch_article_text(e["link"])
                docs, new_docs = add_articles_to_corpus(entries)
                st.info(f"New docs after fallback: {len(new_docs)}")
                chunks = rebuild_vectorstore_from_docs(docs)
            st.success(f"Indexed {len(new_docs)} new article(s). Total chunks: {chunks}")
        except Exception as e:
            st.error("Indexing failed.")
            st.exception(e)

with col2:
    if st.button("📨 Send Latest Digest to Telegram"):
        try:
            with st.spinner("Building & sending digest…"):
                entries = fetch_rss_entries(FEEDS)
                for e in entries:
                    e["full_text"] = fetch_article_text(e["link"])
                docs, new_docs = add_articles_to_corpus(entries)
                if new_docs:
                    parts = []
                    for d in new_docs[:5]:
                        s = summarize_article(d["title"], d["text"])
                        parts.append(f"• <b>{d['title']}</b>\n{s}\n\n🔗 {d['link']}")
                    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
                    send_telegram_message(digest[:3900])
                    st.success("Digest sent to Telegram.")
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
