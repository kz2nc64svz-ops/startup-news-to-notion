import os, feedparser, json, requests, hashlib




def build_notion_children(items):
children = []
for it in items:
text = f"{it.get('title')} — {it.get('summary')}\nTags: {it.get('tags')} | Importance: {it.get('importance')}\n{it.get('link')}"
children.append({
'object': 'block',
'type': 'paragraph',
'paragraph': {
'rich_text': [{'type': 'text', 'text': {'content': text}}]
}
})
return children




def post_to_notion(items):
now = datetime.now().strftime('%Y-%m-%d')
title = f"📰 Startup News Digest — {now}"
page_data = {
'parent': {'type':'page_id','page_id': NOTION_PAGE_ID},
'properties': {
'title': {'title': [{'text': {'content': title}}]}
},
'children': build_notion_children(items)
}
res = requests.post('https://api.notion.com/v1/pages',
headers={
'Authorization': f'Bearer {NOTION_TOKEN}',
'Content-Type': 'application/json',
'Notion-Version': '2022-06-28'
},
json=page_data)
if res.status_code not in (200,201):
raise RuntimeError(f"Notion API error: {res.status_code} {res.text}")
return res.json()




def main():
seen = load_seen()
entries = collect_entries()
# dedupe
new_entries = []
for e in entries:
fp = fingerprint(e)
if fp not in seen:
seen.add(fp)
new_entries.append(e)


if not new_entries:
print('No new entries to process.')
save_seen(seen)
return


items = summarize_with_gpt(new_entries)
if not items:
print('No items after filtering')
save_seen(seen)
return


post_to_notion(items)
save_seen(seen)
print('Posted digest to Notion')


if __name__ == '__main__':
main()
