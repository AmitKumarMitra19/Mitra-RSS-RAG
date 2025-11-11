# src/loader.py
import time
import re
import feedparser
import trafilatura
import requests

# Optional Streamlit cache (no-op outside Streamlit)
try:
    import streamlit as st
    cache_data = st.cache_data
except Exception:
    def cache_data(func):  # no-op
        return func

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s

@cache_data(ttl=600)
def fetch_rss_entries(feed_urls):
    """Return list of dicts: title, link, published(epoch), summary"""
    out = []
    for url in feed_urls:
        try:
            fp = feedparser.parse(url)
            for e in fp.entries:
                link = getattr(e, "link", "")
                title = clean_text(getattr(e, "title", ""))
                summary = clean_text(getattr(e, "summary", ""))
                if hasattr(e, "published_parsed") and e.published_parsed:
                    ts = time.mktime(e.published_parsed)
                else:
                    ts = time.time()
                if link:
                    out.append({"title": title, "link": link, "summary": summary, "published": ts})
        except Exception:
            # Skip bad feeds but don't crash the app
            continue
    # de-dup by link
    seen = set()
    dedup = []
    for item in out:
        if item["link"] and item["link"] not in seen:
            dedup.append(item)
            seen.add(item["link"])
    dedup.sort(key=lambda x: x["published"], reverse=True)
    return dedup

# Session with UA + timeouts to reduce 403/SSL flakiness
def _session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; RSS-RAG/1.0; +https://streamlit.io)"
    })
    return s

@cache_data(ttl=1200)
def fetch_article_text(url: str, timeout=15) -> str:
    """Use trafilatura for robust extraction; fallback to raw text."""
    if not url:
        return ""
    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            # Fallback: raw GET with UA
            try:
                r = _session().get(url, timeout=timeout)
                r.raise_for_status()
                return clean_text(r.text)
            except Exception:
                return ""
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False
        ) or ""
        if not text.strip():
            # Fallback to raw HTML text if extraction failed
            try:
                r = _session().get(url, timeout=timeout)
                r.raise_for_status()
                return clean_text(r.text)
            except Exception:
                return ""
        return clean_text(text)
    except Exception:
        # Never crash caller—just return empty
        return ""
