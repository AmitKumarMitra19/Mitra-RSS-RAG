# src/config.py
import os

def _get(key, default=""):
    return os.getenv(key, default)

# Feeds (you can override in Secrets)
DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
]
FEEDS = [s.strip() for s in _get("RSS_FEEDS", "").split(",") if s.strip()] or DEFAULT_FEEDS

# Telegram
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = _get("TELEGRAM_CHAT_ID", "")

# Lite switches (force stability)
USE_RSS_SUMMARY_ONLY = _get("USE_RSS_SUMMARY_ONLY", "1").lower() in ("1","true","yes")  # no page fetch
DISABLE_SUMMARIZER   = _get("DISABLE_SUMMARIZER", "1").lower() in ("1","true","yes")    # no HF models
DISABLE_EMBEDDINGS   = _get("DISABLE_EMBEDDINGS", "1").lower() in ("1","true","yes")    # no FAISS/index

# Models (kept for completeness; unused in lite)
EMB_MODEL = _get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SUM_MODEL = _get("SUM_MODEL", "sshleifer/distilbart-cnn-12-6")
TOP_K = int(_get("TOP_K", 5))

# HARD caps
MAX_FEEDS                = int(_get("MAX_FEEDS", 2))
PER_FEED_LIMIT           = int(_get("PER_FEED_LIMIT", 3))
OVERALL_ENTRY_LIMIT      = int(_get("OVERALL_ENTRY_LIMIT", 6))
MAX_NEW_DOCS_PER_RUN     = int(_get("MAX_NEW_DOCS_PER_RUN", 6))
MAX_SUMMARY_ITEMS_IN_DIGEST = int(_get("MAX_SUMMARY_ITEMS_IN_DIGEST", 3))
MAX_CHUNKS_FOR_EMBED     = int(_get("MAX_CHUNKS_FOR_EMBED", 1000))

# Rate limiting (gentle)
FEED_DELAY_MS   = int(_get("FEED_DELAY_MS", 400))
ITEM_DELAY_MS   = int(_get("ITEM_DELAY_MS", 150))
REQUEST_TIMEOUT_S = float(_get("REQUEST_TIMEOUT_S", "8"))
MAX_RETRIES     = int(_get("MAX_RETRIES", 2))
BACKOFF_BASE_S  = float(_get("BACKOFF_BASE_S", "0.8"))

# Storage
DATA_DIR  = _get("DATA_DIR", "./data")
INDEX_DIR = os.path.join(DATA_DIR, "index")
DOCS_JSON = os.path.join(DATA_DIR, "docs.json")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
EMB_NPY    = os.path.join(INDEX_DIR, "embeddings.npy")
