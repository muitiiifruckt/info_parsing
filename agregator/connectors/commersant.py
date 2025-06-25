# Скрипт для сбора данных с сайта "Коммерсант"
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import feedparser
from datetime import datetime, timedelta
from ..config_schema import SectionsUrlRSS, NewsItem, SearchConfig
from ..config import ag_conf_1


### определение ссылок для разных разделов
cm_urls = SectionsUrlRSS(
main = 'https://www.kommersant.ru/RSS/news.xml',
business = "https://www.kommersant.ru/RSS/section-business.xml",
economics = "https://www.kommersant.ru/RSS/section-economics.xml",
financess = "https://www.kommersant.ru/RSS/money.xml"
)
### определение ссылок для разных разделов
source = "Kommersant"
###########

####### получение новостей с ссылок


def get_itemns(link_type: str, timedelta: datetime) -> list[NewsItem]:
    """ Собирает статьи за последние timedelta времени по типу link_type"""
    News = []
    feed = feedparser.parse(link_type)
    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6])
        if published >= timedelta:
            News.append(NewsItem(
                time=published.strftime('%Y-%m-%d'),
                title=entry.title,
                link=entry.link,
                source=source,
                description = entry.description,
                body=None
            ))
    return News
def get_all_itemns(link_types: str, timedelta: datetime) -> list[NewsItem]:
    """Собирает все статьи с сайта с учетом разных типов статей"""
    all_news = []
    for link in link_types:
        news = get_itemns(getattr(cm_urls, link),timedelta)
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
        article_text = soup.find_all('p', class_='doc__text')
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

def filter_items(news:list[NewsItem], emitents: list[str], search_within: bool) -> list[NewsItem]:
    """ Ищет в статье упоминание эмитента и присваевает статье эмитент, затем
           отсеивает статье без эмитентов"""
    
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
        if new.emitent is not None:
            news_filtered.append(new)
            
    return news_filtered
            
            
        
    
def get_filtered_items(config: SearchConfig) ->list[NewsItem]:
    """Фильтрация статей по параметрам конфига"""
    
    timeedelta = datetime.now() - timedelta(hours=config.time_delta_hours)
    search_within = config.search_within
    emitents = config.emitent
    link_types = config.search_sections
    
    news = get_all_itemns(link_types,timeedelta)

    filtered_news = filter_items(news,emitents,search_within)
    return filtered_news


if __name__ == '__main__':
    news = get_filtered_items(ag_conf_1)
    print(news)
    print(len(news))
