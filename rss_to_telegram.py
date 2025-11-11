# rss_to_telegram.py
from src.config import MAX_SUMMARY_ITEMS_IN_DIGEST
from src.loader import fetch_rss_entries
from src.indexer import add_articles_to_corpus, load_docs
from src.summarize import summarize_article
from src.push import send_telegram_message

def build_items():
    entries = fetch_rss_entries([])  # FEEDS read inside loader via config
    docs, new_docs = add_articles_to_corpus(entries)
    if new_docs:
        items = new_docs[:MAX_SUMMARY_ITEMS_IN_DIGEST]
        source = "new"
    else:
        all_docs = load_docs()
        items = sorted(all_docs, key=lambda d: d.get("published", 0), reverse=True)[:MAX_SUMMARY_ITEMS_IN_DIGEST]
        source = "stored"
    return items, source

def main():
    items, source = build_items()
    if not items:
        print("Nothing to send.")
        return
    parts = []
    for d in items:
        s = summarize_article(d["title"], d.get("text", ""))
        parts.append(f"• <b>{d['title']}</b>\n{s}\n\n🔗 {d['link']}")
    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
    send_telegram_message(digest[:3900])
    print(f"Digest sent from {source} items: {len(items)}")

if __name__ == "__main__":
    main()
