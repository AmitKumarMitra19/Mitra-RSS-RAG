import os

DEFAULT_FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]

FEEDS = [s.strip() for s in os.getenv("RSS_FEEDS", "").split(",") if s.strip()] or DEFAULT_FEEDS

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# Models (good on Colab T4)
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SUM_MODEL = os.getenv("SUM_MODEL", "facebook/bart-large-cnn")

TOP_K = int(os.getenv("TOP_K", 5))

DATA_DIR = os.getenv("DATA_DIR", "./data")
INDEX_DIR = os.path.join(DATA_DIR, "index")
DOCS_JSON = os.path.join(DATA_DIR, "docs.json")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
EMB_NPY = os.path.join(INDEX_DIR, "embeddings.npy")
