import time
import re
import feedparser
import trafilatura
import requests

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s

def fetch_rss_entries(feed_urls):
    """Return list of dicts: title, link, published(epoch), summary"""
    out = []
    for url in feed_urls:
        fp = feedparser.parse(url)
        for e in fp.entries:
            link = getattr(e, "link", "")
            title = clean_text(getattr(e, "title", ""))
            summary = clean_text(getattr(e, "summary", ""))
            if hasattr(e, "published_parsed") and e.published_parsed:
                ts = time.mktime(e.published_parsed)
            else:
                ts = time.time()
            out.append({"title": title, "link": link, "summary": summary, "published": ts})
    # de-dup by link
    seen = set()
    dedup = []
    for item in out:
        if item["link"] and item["link"] not in seen:
            dedup.append(item)
            seen.add(item["link"])
    dedup.sort(key=lambda x: x["published"], reverse=True)
    return dedup

def fetch_article_text(url: str, timeout=15) -> str:
    """Use trafilatura; fallback to raw HTML."""
    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
        return clean_text(text)
    except Exception:
        try:
            r = requests.get(url, timeout=timeout)
            return clean_text(r.text)
        except Exception:
            return ""
