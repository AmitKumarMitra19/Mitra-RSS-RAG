# 📰 RSS RAG → Telegram Digest

A lightweight system that **fetches RSS feeds, summarizes new articles, and sends daily digests to Telegram** — powered by **Python, Streamlit, and GitHub Actions**.

---

## 🚀 Features
- Fetches multiple RSS feeds and detects new updates  
- Summarizes articles (or uses RSS summaries in Lite mode)  
- Sends formatted digests via Telegram Bot  
- Runs automatically on schedule using GitHub Actions  
- Streamlit app for manual testing and live updates  

---

## ⚙️ Setup Instructions

### 🔧 Requirements
- Python 3.11 or later  
- GitHub account  
- Telegram Bot Token and Chat ID  
- Streamlit Cloud (for optional deployment)

---

### 🔐 Configure Secrets

Add the following secrets either in **Streamlit → Settings → Secrets** or **GitHub → Settings → Secrets and variables → Actions**:

```toml
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id_or_@channel"
RSS_FEEDS = "https://feeds.bbci.co.uk/news/world/rss.xml, https://www.theverge.com/rss/index.xml"
USE_RSS_SUMMARY_ONLY = "1"
DISABLE_SUMMARIZER = "1"
DISABLE_EMBEDDINGS = "1"

**### 🕒 GitHub Actions Automation**

- This project includes an automated workflow to fetch feeds and send Telegram digests on schedule.

- Workflow file: .github/workflows/rss_digest.yml

**This action automatically:**

- Fetches latest RSS feeds
- Detects new articles
- Summarizes them
- Sends a Telegram digest

If no new updates are found, it logs “Nothing to send.”

StreamLit App: https://mitra-rss-rag.streamlit.app/
