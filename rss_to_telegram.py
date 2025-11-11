# rss_to_telegram.py
from src.config import FEEDS, MAX_SUMMARY_ITEMS_IN_DIGEST
from src.loader import fetch_rss_entries
from src.indexer import add_articles_to_corpus, load_docs
from src.summarize import summarize_article
from src.push import send_telegram_message

def pick_items():
    # 1) Fetch from FEEDS (from GitHub Secrets -> env -> config)
    entries = fetch_rss_entries(FEEDS)
    print(f"[CI] fetched entries: {len(entries)}")

    # 2) Add new docs (Lite mode stores summaries)
    docs, new_docs = add_articles_to_corpus(entries)
    print(f"[CI] new_docs added: {len(new_docs)}  total_docs: {len(docs)}")

    # 3) Prefer new docs; otherwise latest stored
    if new_docs:
        items = new_docs[:MAX_SUMMARY_ITEMS_IN_DIGEST]
        source = "new"
    else:
        all_docs = load_docs()
        items = sorted(all_docs, key=lambda d: d.get("published", 0), reverse=True)[:MAX_SUMMARY_ITEMS_IN_DIGEST]
        source = "stored"
    print(f"[CI] using {len(items)} items from: {source}")
    return items, source

def main():
    items, source = pick_items()
    if not items:
        print("[CI] No items to send.")
        return
    parts = []
    for d in items:
        s = summarize_article(d.get("title",""), d.get("text",""))
        parts.append(f"• <b>{d.get('title','(untitled)')}</b>\n{s}\n\n🔗 {d.get('link','')}")
    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
    send_telegram_message(digest[:3900])
    print(f"[CI] Digest sent ({len(items)} items, source={source}).")

if __name__ == "__main__":
    main()
