import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import feedparser
from datetime import datetime, timedelta
from ..config_schema import SectionsUrlRSS, NewsItem, SearchConfig
from ..config import ag_conf_1
from .rss_parser import save_news_to_txt

# определение ссылок для разных разделов
vedomosti_urls = SectionsUrlRSS(
    main="http://www.vedomosti.ru/newsline/out/rss.xml",
    business="http://www.vedomosti.ru/rss/rubric/business.xml",
    economics="http://www.vedomosti.ru/rss/rubric/economics.xml",
    financess="http://www.vedomosti.ru/rss/rubric/finance.xml"
)
source = "Vedomosti"

def get_itemns(link_type: str, timedelta_dt: datetime) -> list[NewsItem]:
    """Собирает статьи за последние timedelta времени по типу link_type"""
    News = []
    feed = feedparser.parse(link_type)
    for entry in feed.entries:
        # pubDate: Fri, 20 Jun 2025 11:40:47 +0300
        try:
            published = datetime(*entry.published_parsed[:6])
        except Exception:
            continue
        if published >= timedelta_dt:
            News.append(NewsItem(
                time=published.strftime('%Y-%m-%d %H:%M'),
                title=entry.title,
                link=entry.link,
                source=source,
                description=getattr(entry, "summary", None),
                body=None
            ))
    return News

def get_all_itemns(link_types: list[str], timedelta_dt: datetime) -> list[NewsItem]:
    """Собирает все статьи с сайта с учетом разных типов статей"""
    all_news = []
    for link in link_types:
        news = get_itemns(getattr(vedomosti_urls, link), timedelta_dt)
        all_news.extend(news)
    return all_news

def set_article_content(item: NewsItem) -> NewsItem:
    """По ссылке статьи достает текст статьи и присывает его в поле"""
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        url = item.link
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        #### поиск текста по тегам и классу
        article_text = soup.find_all('p', class_='box-paragraph__text')
        
        ### поиск текста по тегам и классу
        text = ""
        for part in article_text:
            text +=part.get_text(strip=True)
        if text:
            item.body = text
        return item
    except Exception as e:
        print(f"Ошибка при получении статьи {url}: {e}")
        return None

def filter_items(news: list[NewsItem], emitents: list[str], search_within: bool) -> list[NewsItem]:
    """Ищет в статье упоминание эмитента и присваивает статье эмитент, затем
       отсеивает статьи без эмитентов"""
    for new in news:
        if search_within:
            new = set_article_content(new)
            for emitent in emitents:
                if new.body and emitent.lower() in new.body.lower():
                    new.emitent = emitent
                    break
        else:
            for emitent in emitents:
                if emitent.lower() in new.title.lower():
                    new.emitent = emitent
                    break
    news_filtered = []
    for new in news:
        if getattr(new, 'emitent', None) is not None:
            news_filtered.append(new)
    return news_filtered

def get_filtered_items(config: SearchConfig) -> list[NewsItem]:
    """Фильтрация статей по параметрам конфига"""
    timedelta_dt = datetime.now() - timedelta(hours=config.time_delta_hours)
    search_within = config.search_within
    emitents = config.emitent
    link_types = config.search_sections
    
    news = get_all_itemns(link_types, timedelta_dt)
    filtered_news = filter_items(news, emitents, search_within)
    return filtered_news



if __name__ == '__main__':
    news = get_filtered_items(ag_conf_1)
    save_news_to_txt(news)
    print(news)
    print(len(news))
    
