# daily_startup_to_notion.py
# Safe, minimal script that logs errors so GitHub Actions shows useful output.

import os
import sys
import time
import requests
import feedparser

def env_or_exit(name):
    v = os.environ.get(name)
    if not v:
        print(f"ERROR: required environment variable {name} is missing.", file=sys.stderr)
        sys.exit(2)
    return v

def add_to_notion(title, url, notion_token, notion_page_id):
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    parent = {"type": "page_id", "page_id": notion_page_id}
    data = {
        "parent": parent,
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data, timeout=20)
    print(f"Notion POST status: {resp.status_code}")
    print("Notion response body:", resp.text)
    if resp.status_code >= 400:
        print("Notion API returned error. Exiting.", file=sys.stderr)
        sys.exit(3)

def main():
    NOTION_TOKEN = env_or_exit("NOTION_TOKEN")
    NOTION_PAGE_ID = env_or_exit("NOTION_PAGE_ID")
    feed_url = os.environ.get("FEED_URL", "https://techcrunch.com/feed/")

    print("Fetching feed:", feed_url)
    feed = feedparser.parse(feed_url)
    if not getattr(feed, "entries", None):
        print("No entries found in feed; exiting.")
        return

    for entry in feed.entries[:5]:
        title = entry.get("title", "Untitled")
        link = entry.get("link", "")
        print("Adding:", title, link)
        try:
            add_to_notion(title, link, NOTION_TOKEN, NOTION_PAGE_ID)
        except Exception as e:
            print("Exception while adding to Notion:", repr(e), file=sys.stderr)
            sys.exit(4)
        time.sleep(1)

    print("Done.")

if __name__ == "__main__":
    main()

