# agregator/connectors/rss_parser.py
import feedparser
from datetime import datetime, timedelta
from ..config_schema import NewsItem
import requests
from bs4 import BeautifulSoup

def fetch_article_body(url: str, source:str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Универсально: собрать все <p> (можно доработать под конкретные сайты)
        if source=="РИА Новости" or source=="Российская газета":
            paragraphs = soup.find_all('div', "class=")
            text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            pass
            paragraphs = soup.find_all('p')
            text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return text if text else None
    except Exception as e:
        print(f"Ошибка при получении статьи {url}: {e}")
        return None

def parse_rss(feed_url: str, source: str, emitents: list, search_within: bool = True) -> list[NewsItem]:
    feed = feedparser.parse(feed_url)
    news = []
    for entry in feed.entries:
        curr_emitent = None
        try:
            published = datetime(*entry.published_parsed[:6])
        except Exception:
            continue
        try:
            link = entry.get('link', '')
            print(link)
            body = fetch_article_body(link) if link else None
            title = entry.get('title', 'Без заголовка')
            add_news = False

            if search_within:
                if body:
                    for emitent in emitents:
                        if emitent.lower() in body.lower():
                            curr_emitent = emitent
                            add_news = True
                            break
            else:
                for emitent in emitents:
                    if emitent.lower() in title.lower():
                        curr_emitent = emitent
                        add_news = True
                        break

            if add_news:
                news.append(NewsItem(
                    time=published.strftime('%Y-%m-%d %H:%M'),
                    title=title,
                    link=link,
                    emitent=curr_emitent,
                    source=source,
                    description=None,
                    body=body
                ))
        except Exception:
            continue
    return news