import os

DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://www.engadget.com/rss.xml",
]

def _get_env(key, default=""):
    return os.getenv(key, default)

FEEDS = [s.strip() for s in _get_env("RSS_FEEDS", "").split(",") if s.strip()] or DEFAULT_FEEDS

TELEGRAM_BOT_TOKEN = _get_env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = _get_env("TELEGRAM_CHAT_ID", "")

# Models (Cloud-safe defaults; can override via secrets)
EMB_MODEL = _get_env("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SUM_MODEL = _get_env("SUM_MODEL", "sshleifer/distilbart-cnn-12-6")  # lighter than bart-large-cnn

TOP_K = int(_get_env("TOP_K", 5))

# Safety limits to avoid OOM/timeouts on Streamlit Cloud
MAX_FEED_ENTRIES_PER_RUN   = int(_get_env("MAX_FEED_ENTRIES_PER_RUN", 80))   # cap fetched entries processed
MAX_NEW_DOCS_PER_RUN       = int(_get_env("MAX_NEW_DOCS_PER_RUN", 30))       # cap how many new docs to add
MAX_SUMMARY_ITEMS_IN_DIGEST= int(_get_env("MAX_SUMMARY_ITEMS_IN_DIGEST", 5)) # cap items in digest
MAX_CHUNKS_FOR_EMBED       = int(_get_env("MAX_CHUNKS_FOR_EMBED", 4000))     # cap total chunks per build

DATA_DIR = _get_env("DATA_DIR", "./data")
INDEX_DIR = os.path.join(DATA_DIR, "index")
DOCS_JSON = os.path.join(DATA_DIR, "docs.json")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
EMB_NPY = os.path.join(INDEX_DIR, "embeddings.npy")
