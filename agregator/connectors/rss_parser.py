# agregator/connectors/rss_parser.py
import feedparser
from datetime import datetime, timedelta
from ..config_schema import NewsItem
import requests
from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt

def save_news_to_txt(news_list, txt_filename="all_news.txt",):
    with open(txt_filename, "a", encoding="utf-8") as f:
        for item in news_list:
            f.write(f"Название: {item.title}\n")
            f.write(f"Источник: {item.source}\n")
            f.write(f"Ссылка: {item.link}\n")
            f.write(f"Эмитент: {item.emitent}\n")
            f.write("Статья:\n")
            if item.body:
                f.write(item.body.strip() + "\n")
            f.write("\n---\n\n")  # Добавляем ссылку в список сохранённых
@retry(stop=stop_after_attempt(3))
def fetch_article_body(url: str, source:str) -> str | None:
    try:
        headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Referer": "https://www.google.com/",
                    "Upgrade-Insecure-Requests": "1",
                }

                        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print()
        print()
        print()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup and len(soup) > 40:
            print("Разметка успешно получена")
        else:
            print("Разметка не получена")
        # Универсально: собрать все <p> (можно доработать под конкретные сайты)
        if source== "РИА Новости":
            paragraphs = soup.find_all('div', class_='article__text')
            text = '\n'.join(p.get_text() for p in paragraphs if p.get_text(strip=True))
        elif source == "Российская газета":
            text = soup.find('div', class_="PageArticleContent_lead__l9TkG commonArticle_zoom__SDMjc").get_text() + " "
            paragraphs = soup.find_all('p')
            text += '\n'.join(p.get_text() for p in paragraphs if p.get_text(strip=True))
        elif source == "ТАСС":
            # 1) Лид берём из метатегов (устойчиво к смене классов)
            lead = None
            og = soup.find("meta", attrs={"property": "og:description"})
            if og and og.get("content"):
                lead = og["content"].strip()
            else:
                md = soup.find("meta", attrs={"name": "description"})
                if md and md.get("content"):
                    lead = md["content"].strip()

            # 2) Основной текст — абзацы внутри <article>, если есть
            paragraphs = []
            article_tag = soup.find("article")
            if article_tag:
                paragraphs = article_tag.find_all("p")
            else:
                # запасной вариант: любые <p>, но без пустых
                paragraphs = soup.find_all("p")

            body_text = '\n'.join(
                p.get_text(" ", strip=True)
                for p in paragraphs
                if p and p.get_text(strip=True)
            )

            text = ((lead + ". ") if lead else "") + body_text
        else:
            paragraphs = soup.find_all('p')
            text = '\n'.join(p.get_text() for p in paragraphs if p.get_text(strip=True))
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
        r"Любое использование материалов допускается только при соблюдении*",
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
    print(fetch_article_body("https://tass.ru/ekonomika/24461943","ТАСС"))