# RSS RAG → Telegram

Pipeline:
1) Read RSS
2) Extract articles (trafilatura)
3) Build FAISS index (sentence-transformers)
4) Summarize (BART)
5) Send Telegram digest
6) Streamlit UI for manual refresh, digest, and RAG search

## Env (set in host/Cloud)
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- RSS_FEEDS (optional, comma-separated)
- EMB_MODEL (optional)
- SUM_MODEL (optional)

## Run
python rss_to_telegram.py
streamlit run app_streamlit.py
