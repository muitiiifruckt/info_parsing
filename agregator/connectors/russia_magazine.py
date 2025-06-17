import feedparser
from datetime import datetime, timedelta

RSS_URL = 'https://rg.ru/xml/index.xml'
feed = feedparser.parse(RSS_URL)

cutoff = datetime.now() - timedelta(days=2)

for entry in feed.entries:
    if 'published_parsed' in entry:
        published = datetime(*entry.published_parsed[:6])
        if published >= cutoff:
            title = entry.get('title', 'Без заголовка')
            link = entry.get('link', 'Без ссылки')
            print(f"{published:%Y-%m-%d %H:%M} — {title}")
            print("→", link, "\n")
