# src/loader.py
import time
import re
import math
import feedparser
import trafilatura
import requests

from src.config import (
    MAX_FEEDS, PER_FEED_LIMIT, OVERALL_ENTRY_LIMIT,
    FEED_DELAY_MS, ITEM_DELAY_MS,
    REQUEST_TIMEOUT_S, MAX_RETRIES, BACKOFF_BASE_S,
)

# Optional Streamlit cache (no-op outside Streamlit)
try:
    import streamlit as st
    cache_data = st.cache_data
except Exception:
    def cache_data(f): return f

def clean_text(s: str) -> str:
    if not s: return ""
    return re.sub(r"\s+", " ", s).strip()

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; RSS-RAG/1.0; +https://streamlit.io)"
    })
    return s

def _sleep_ms(ms: int):
    if ms and ms > 0:
        time.sleep(ms / 1000.0)

def _with_retries(fn, *args, **kwargs):
    """
    Run fn with retries + exponential backoff (jitter-free).
    Returns fn() result or raises last exception.
    """
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            # backoff: base^(attempt) seconds (capped)
            backoff = BACKOFF_BASE_S ** attempt
            time.sleep(min(2.5, backoff))
    if last_exc:
        raise last_exc

@cache_data(ttl=600)
def fetch_rss_entries(feed_urls):
    """
    Fetch RSS items with strict caps and rate-limits:
      - process up to MAX_FEEDS feeds
      - take first PER_FEED_LIMIT items from each
      - stop after OVERALL_ENTRY_LIMIT total
      - sleep FEED_DELAY_MS between feeds and ITEM_DELAY_MS between items
    """
    total_cap = OVERALL_ENTRY_LIMIT
    out = []
    feeds = list(feed_urls)[:MAX_FEEDS]

    for fidx, url in enumerate(feeds, 1):
        try:
            # feedparser is local; add a small delay between feeds
            fp = feedparser.parse(url)
            items = fp.entries[:PER_FEED_LIMIT]
            for iidx, e in enumerate(items, 1):
                # intra-feed delay
                _sleep_ms(ITEM_DELAY_MS)
                link = getattr(e, "link", "")
                if not link:
                    continue
                title = clean_text(getattr(e, "title", ""))
                summary = clean_text(getattr(e, "summary", ""))
                if hasattr(e, "published_parsed") and e.published_parsed:
                    ts = time.mktime(e.published_parsed)
                else:
                    ts = time.time()
                out.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": ts
                })
                if len(out) >= total_cap:
                    break
        except Exception:
            # ignore one bad feed
            pass
        if len(out) >= total_cap:
            break
        # inter-feed delay
        _sleep_ms(FEED_DELAY_MS)

    # de-dup + sort
    seen, dedup = set(), []
    for item in out:
        if item["link"] not in seen:
            dedup.append(item); seen.add(item["link"])
    dedup.sort(key=lambda x: x["published"], reverse=True)
    return dedup

@cache_data(ttl=1200)
def fetch_article_text(url: str) -> str:
    """
    Best-effort article extraction with retry/backoff and UA. Callers may skip this
    entirely when USE_RSS_SUMMARY_ONLY is on.
    """
    if not url:
        return ""
    sess = _session()

    def _get_html():
        r = sess.get(url, timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        return r.text

    # Try trafilatura first, then raw HTML, with retries
    try:
        downloaded = _with_retries(trafilatura.fetch_url, url, timeout=REQUEST_TIMEOUT_S)
        if not downloaded:
            html = _with_retries(_get_html)
            return clean_text(html)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
        if not text.strip():
            html = _with_retries(_get_html)
            return clean_text(html)
        return clean_text(text)
    except Exception:
        # never crash caller
        try:
            html = _with_retries(_get_html)
            return clean_text(html)
        except Exception:
            return ""
