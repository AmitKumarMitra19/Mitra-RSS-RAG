import sys
from src.indexer import search

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python search_cli.py "your question"')
        sys.exit(1)
    q = sys.argv[1]
    hits = search(q, top_k=5)
    for h in hits:
        print(f"[{h['rank']}] {h['title']}  (score={h['score']:.3f})")
        print(h["chunk"][:300], "...")
        print(h["link"])
        print("-"*80)
