from src.config import FEEDS
from src.loader import fetch_rss_entries, fetch_article_text
from src.indexer import add_articles_to_corpus, rebuild_vectorstore_from_docs
from src.summarize import summarize_article
from src.push import send_telegram_message

def collect_and_index():
    entries = fetch_rss_entries(FEEDS)
    print(f"Fetched {len(entries)} feed entries.")
    # hydrate full text
    for e in entries:
        e["full_text"] = fetch_article_text(e["link"])
    docs, new_docs = add_articles_to_corpus(entries)
    print(f"Add-to-corpus: {len(new_docs)} new docs after fallback.")
    if new_docs:
        total_chunks = rebuild_vectorstore_from_docs(docs)
        print(f"Indexed: {len(new_docs)} new articles, {total_chunks} total chunks.")
    else:
        print("No new articles this run.")
    return new_docs

def build_digest(new_docs, limit=5):
    if not new_docs:
        return None
    items = new_docs[:limit]
    parts = []
    for d in items:
        s = summarize_article(d["title"], d["text"])
        parts.append(f"• <b>{d['title']}</b>\n{s}\n\n🔗 {d['link']}")
    digest = "<b>📰 RSS Digest</b>\n\n" + "\n\n".join(parts)
    return digest[:3900]  # Telegram safety

def main():
    new_docs = collect_and_index()
    digest = build_digest(new_docs)
    if digest:
        send_telegram_message(digest)
        print("Digest sent to Telegram.")
    else:
        print("Nothing new to send.")

if __name__ == "__main__":
    main()
