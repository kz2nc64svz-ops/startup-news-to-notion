# daily_startup_to_notion.py
# Automatically adds top 5 TechCrunch startup news to Notion.

import os
import sys
import time
import requests
import feedparser

def env_or_exit(name):
    """Ensure required environment variables exist."""
    v = os.environ.get(name)
    if not v:
        print(f"ERROR: required environment variable {name} is missing.", file=sys.stderr)
        sys.exit(2)
    return v

def add_to_notion(title, url, notion_token, notion_page_id):
    """Send a new page to Notion."""
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"type": "page_id", "page_id": notion_page_id},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url}
        }
    }

    resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data, timeout=20)
    print(f"Notion POST status: {resp.status_code}")
    print("Response body:", resp.text)

    if resp.status_code >= 400:
        print("Notion API returned an error, exiting.", file=sys.stderr)
        sys.exit(3)

def main():
    """Main script logic."""
    notion_token = env_or_exit("NOTION_TOKEN")
    notion_page_id = env_or_exit("NOTION_PAGE_ID")

    feed_url = "https://techcrunch.com/feed/"
    print(f"Fetching feed from: {feed_url}")
    feed = feedparser.parse(feed_url)

    if not getattr(feed, "entries", None):
        print("No entries found in the feed; exiting.")
        return

    for entry in feed.entries[:5]:
        title = entry.get("title", "Untitled")
        link = entry.get("link", "")
        print(f"Adding: {title} -> {link}")
        try:
            add_to_notion(title, link, notion_token, notion_page_id)
        except Exception as e:
            print(f"Exception while adding to Notion: {e}", file=sys.stderr)
            sys.exit(4)
        time.sleep(1)  # Avoid rate limits

    print("✅ Done — all top 5 items added to Notion.")

if __name__ == "__main__":
    main()
