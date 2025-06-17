import feedparser
from datetime import datetime, timedelta

RSS_URL = 'https://tass.ru/rss/v2.xml'  # Можно заменить на любую тему
feed = feedparser.parse(RSS_URL)

cutoff = datetime.now() - timedelta(days=2)

for entry in feed.entries:
    if 'published_parsed' in entry:
        published = datetime(*entry.published_parsed[:6])
        if published >= cutoff:
            print(f"{published:%Y-%m-%d %H:%M} — {entry.title}")
            print("→", entry.link)
            print()
