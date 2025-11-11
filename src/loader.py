# src/loader.py
import time, re
import feedparser
import requests
from src.config import (
    MAX_FEEDS, PER_FEED_LIMIT, OVERALL_ENTRY_LIMIT,
    FEED_DELAY_MS, ITEM_DELAY_MS, REQUEST_TIMEOUT_S,
    MAX_RETRIES, BACKOFF_BASE_S
)

try:
    import streamlit as st
    cache_data = st.cache_data
except Exception:
    def cache_data(f): return f

def clean_text(s: str) -> str:
    if not s: return ""
    return re.sub(r"\s+", " ", s).strip()

def _sleep_ms(ms: int):
    if ms and ms > 0:
        time.sleep(ms/1000.0)

def _session():
    s = requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; RSS-RAG/1.0)"})
    return s

def _with_retries(fn, *a, **k):
    last = None
    for i in range(MAX_RETRIES):
        try:
            return fn(*a, **k)
        except Exception as e:
            last = e
            time.sleep(min(2.5, BACKOFF_BASE_S**i))
    if last: raise last

@cache_data(ttl=600)
def fetch_rss_entries(feed_urls):
    out, total_cap = [], OVERALL_ENTRY_LIMIT
    for url in list(feed_urls)[:MAX_FEEDS]:
        try:
            fp = feedparser.parse(url)
            for e in fp.entries[:PER_FEED_LIMIT]:
                _sleep_ms(ITEM_DELAY_MS)
                link = getattr(e,"link","");  title = clean_text(getattr(e,"title",""))
                if not link: continue
                summary = clean_text(getattr(e,"summary",""))
                ts = time.mktime(e.published_parsed) if hasattr(e,"published_parsed") and e.published_parsed else time.time()
                out.append({"title":title,"link":link,"summary":summary,"published":ts})
                if len(out) >= total_cap: break
        except Exception:
            pass
        if len(out) >= total_cap: break
        _sleep_ms(FEED_DELAY_MS)
    # de-dup & sort
    seen, dedup = set(), []
    for it in out:
        if it["link"] not in seen:
            dedup.append(it); seen.add(it["link"])
    dedup.sort(key=lambda x: x["published"], reverse=True)
    return dedup
