# agregator/connectors/rss_parser.py
import feedparser
from datetime import datetime, timedelta
from ..config_schema import NewsItem

def parse_rss(feed_url: str, source: str, cutoff_hours: int = 1) -> list[NewsItem]:
    feed = feedparser.parse(feed_url)
 
    cutoff = datetime.now() - timedelta(hours=cutoff_hours)
    news = []
    for entry in feed.entries:
        try:
            published = datetime(*entry.published_parsed[:6])
     
        except Exception:
            continue
        try:
            if published >= cutoff:
            
                news.append(NewsItem(
                    time=published.strftime('%Y-%m-%d %H:%M'),
                    title=entry.get('title', 'Без заголовка'),
                
                    link=entry.get('link', ''),
                    source=source,
                    description= None,
                    body=None
                ))
        except Exception:
            continue
    return news