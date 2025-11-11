import time, re
import feedparser
import trafilatura
import requests

# Optional Streamlit cache (no-op outside Streamlit)
try:
    import streamlit as st
    cache_data = st.cache_data
except Exception:
    def cache_data(func): return func

from src.config import MAX_FEEDS, PER_FEED_LIMIT, OVERALL_ENTRY_LIMIT

def clean_text(s: str) -> str:
    if not s: return ""
    return re.sub(r"\s+", " ", s).strip()

def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RSS-RAG/1.0)"})
    return s

@cache_data(ttl=600)
def fetch_rss_entries(feed_urls):
    """
    Pull RSS entries with strict caps:
      - only first MAX_FEEDS feeds
      - only first PER_FEED_LIMIT entries from each
      - stop when OVERALL_ENTRY_LIMIT reached
    """
    out = []
    total_cap = OVERALL_ENTRY_LIMIT
    for url in list(feed_urls)[:MAX_FEEDS]:
        try:
            fp = feedparser.parse(url)
            for e in fp.entries[:PER_FEED_LIMIT]:
                link = getattr(e, "link", "")
                if not link: continue
                title = clean_text(getattr(e, "title", ""))
                summary = clean_text(getattr(e, "summary", ""))
                if hasattr(e, "published_parsed") and e.published_parsed:
                    ts = time.mktime(e.published_parsed)
                else:
                    ts = time.time()
                out.append({"title": title, "link": link, "summary": summary, "published": ts})
                if len(out) >= total_cap:
                    break
        except Exception:
            # ignore bad feed; continue
            pass
        if len(out) >= total_cap:
            break

    # de-dup + sort
    seen, dedup = set(), []
    for item in out:
        if item["link"] not in seen:
            dedup.append(item); seen.add(item["link"])
    dedup.sort(key=lambda x: x["published"], reverse=True)
    return dedup

@cache_data(ttl=1200)
def fetch_article_text(url: str, timeout=12) -> str:
    """Best-effort article extraction; caller may skip this entirely."""
    if not url: return ""
    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            r = _session().get(url, timeout=timeout); r.raise_for_status()
            return clean_text(r.text)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
        if not text.strip():
            r = _session().get(url, timeout=timeout); r.raise_for_status()
            return clean_text(r.text)
        return clean_text(text)
    except Exception:
        return ""
