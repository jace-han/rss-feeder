# bot.py
import os
import json
import feedparser
import requests
from datetime import datetime

# config: read from env (set these as GitHub secrets)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RSS_FEED_URL = os.getenv("RSS_FEED_URLS", "").split(",")
RSS_FEED_URL = [url.strip() for url in RSS_FEED_URL if url.strip()]

# storage file in repo to track seen entries
SEEN_FILE = "seen.json"

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in env.")

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"seen_ids": []}

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_telegram(text, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()

def main():
    seen = load_seen()
    seen_ids = set(seen.get("seen_ids", []))
    new_ids = []

    for url in RSS_FEED_URL:
        print(f"Checking: {url}")
        feed = feedparser.parse(url)
        entries = feed.entries or []
        if not entries:
            continue

        to_notify = []

        for entry in entries:
            entry_id = getattr(entry, "id", None) or entry.get("link") or entry.get("title")
            if entry_id in seen_ids:
                continue
            title = entry.get("title", "No title")
            link = entry.get("link", "")
            pub = entry.get("published", entry.get("updated", ""))
            text = f"📝 <b>{title}</b>\n{link}\n\n<i>{pub}</i>"
            to_notify.append((entry_id, text))
            new_ids.append(entry_id)

        for entry_id, text in reversed(to_notify):
            try:
                send_telegram(text)
                print(f"Sent: {entry_id}")
            except Exception as e:
                print("Failed to send message:", e)

    if new_ids:
        seen_ids.update(new_ids)
        save_seen({"seen_ids": list(seen_ids)})
    else:
        print("No new posts.")


if __name__ == "__main__":
    main()
