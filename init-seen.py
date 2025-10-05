import feedparser
import json

RSS_FEED_URL = os.getenv("RSS_FEED_URL", "").split(",")
RSS_FEED_URL = [url.strip() for url in RSS_FEED_URL if url.strip()]
seen_ids = set()

for url in RSS_FEED_URL:
    feed = feedparser.parse(url)
    entries = feed.entries or []
    for entry in entries:
        entry_id = getattr(entry, "id", None) or entry.get("link") or entry.get("title")
        full_id = f"{url}|{entry_id}"  # ensures uniqueness across feeds
        seen_ids.add(full_id)

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump({"seen_ids": list(seen_ids)}, f, indent=2)

print(f"Initialized seen.json with {len(seen_ids)} entries.")
