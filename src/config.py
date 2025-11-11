# src/config.py
import os

def _get(key, default=""):
    return os.getenv(key, default)

# ---- Feeds ----
DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://www.engadget.com/rss.xml",
]
FEEDS = [s.strip() for s in _get("RSS_FEEDS", "").split(",") if s.strip()] or DEFAULT_FEEDS

# ---- Telegram ----
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = _get("TELEGRAM_CHAT_ID", "")

# ---- Models ----
EMB_MODEL = _get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SUM_MODEL = _get("SUM_MODEL", "sshleifer/distilbart-cnn-12-6")
TOP_K = int(_get("TOP_K", 5))

# ---- Hard caps (keep small for Streamlit Cloud) ----
MAX_FEEDS                  = int(_get("MAX_FEEDS", 3))      # use at most N feeds
PER_FEED_LIMIT             = int(_get("PER_FEED_LIMIT", 4)) # first N items per feed
OVERALL_ENTRY_LIMIT        = int(_get("OVERALL_ENTRY_LIMIT", 12))  # total per run
MAX_NEW_DOCS_PER_RUN       = int(_get("MAX_NEW_DOCS_PER_RUN", 12))
MAX_SUMMARY_ITEMS_IN_DIGEST= int(_get("MAX_SUMMARY_ITEMS_IN_DIGEST", 4))
MAX_CHUNKS_FOR_EMBED       = int(_get("MAX_CHUNKS_FOR_EMBED", 2000))

# ---- Lightweight mode ----
USE_RSS_SUMMARY_ONLY       = _get("USE_RSS_SUMMARY_ONLY", "1").lower() in ("1","true","yes")

# ---- NEW: Rate limiting & retries ----
# Delays are in milliseconds
FEED_DELAY_MS              = int(_get("FEED_DELAY_MS", 400))   # wait between feeds
ITEM_DELAY_MS              = int(_get("ITEM_DELAY_MS", 120))   # wait between items inside a feed

REQUEST_TIMEOUT_S          = float(_get("REQUEST_TIMEOUT_S", "10"))
MAX_RETRIES                = int(_get("MAX_RETRIES", 3))
BACKOFF_BASE_S             = float(_get("BACKOFF_BASE_S", "0.8"))  # exponential backoff base

# ---- Storage ----
DATA_DIR  = _get("DATA_DIR", "./data")
INDEX_DIR = os.path.join(DATA_DIR, "index")
DOCS_JSON = os.path.join(DATA_DIR, "docs.json")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
EMB_NPY    = os.path.join(INDEX_DIR, "embeddings.npy")
