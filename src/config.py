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

# ---- Models (Cloud-safe defaults) ----
EMB_MODEL = _get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SUM_MODEL = _get("SUM_MODEL", "sshleifer/distilbart-cnn-12-6")  # lighter

TOP_K = int(_get("TOP_K", 5))

# ---- HARD LIMITS to prevent overload ----
# Use fewer feeds, fewer entries per feed, and a small overall cap.
MAX_FEEDS                = int(_get("MAX_FEEDS", 4))     # use at most N feeds
PER_FEED_LIMIT           = int(_get("PER_FEED_LIMIT", 5))# first N items per feed
OVERALL_ENTRY_LIMIT      = int(_get("OVERALL_ENTRY_LIMIT", 20)) # total per run
MAX_NEW_DOCS_PER_RUN     = int(_get("MAX_NEW_DOCS_PER_RUN", 20))
MAX_SUMMARY_ITEMS_IN_DIGEST = int(_get("MAX_SUMMARY_ITEMS_IN_DIGEST", 5))
MAX_CHUNKS_FOR_EMBED     = int(_get("MAX_CHUNKS_FOR_EMBED", 2000)) # smaller to keep memory low

# Set to "1" / "true" to avoid fetching article pages; use RSS summaries only (fastest, most robust)
USE_RSS_SUMMARY_ONLY     = _get("USE_RSS_SUMMARY_ONLY", "1").lower() in ("1","true","yes")

# ---- Storage ----
DATA_DIR  = _get("DATA_DIR", "./data")
INDEX_DIR = os.path.join(DATA_DIR, "index")
DOCS_JSON = os.path.join(DATA_DIR, "docs.json")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
EMB_NPY    = os.path.join(INDEX_DIR, "embeddings.npy")
