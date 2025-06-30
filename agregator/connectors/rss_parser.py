# agregator/connectors/rss_parser.py
import feedparser
from datetime import datetime, timedelta
from ..config_schema import NewsItem
import requests
from bs4 import BeautifulSoup
import re

def fetch_article_body(url: str, source:str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Универсально: собрать все <p> (можно доработать под конкретные сайты)
        if source=="РИА Новости":
            paragraphs = soup.find_all('div', class_='article__text')
            text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            paragraphs = soup.find_all('p')
            text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        if text:
            text = clean_article_text(text)
        return text if text else None
    except Exception as e:
        print(f"Ошибка при получении статьи {url}: {e}")
        return None

def clean_article_text(text: str) -> str:
    # Удаляем шапки в начале текста:
    # "МОСКВА, 30 июн - РИА Новости."
    text = re.sub(
        r'^[А-ЯЁA-Z\-]+,\s*\d{1,2}\s+[а-яa-z]+\s*-\s*РИА Новости\.\s*',
        '',
        text,
        flags=re.MULTILINE
    )
    # "МОСКВА, 30 июня. /ТАСС/."
    text = re.sub(
        r'^[А-ЯЁA-Z\-]+,\s*\d{1,2}\s+[а-яa-z]+\.\s*/ТАСС/\.?\s*',
        '',
        text,
        flags=re.MULTILINE
    )
    # Обрезаем по фразе и всем её "хвостам"
    cut_patterns = [
        r"РБК в Telegram.*",
        r"Интернет-портал «Российской газеты».*",
        # другие паттерны для "хвостов"
    ]
    for pattern in cut_patterns:
        match = re.search(pattern, text, flags=re.DOTALL | re.MULTILINE)
        if match:
            text = text[:match.start()]
    # Удаляем лишние пустые строки
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

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
            body = fetch_article_body(link,source=source) if link else None
            print(body)
            title = entry.get('title', 'Без заголовка')
            print(title)
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
if __name__ == '__main__':
    print(fetch_article_body("https://tass.ru/mezhdunarodnaya-panorama/24390549","Tass"))