# Скрипт для сбора данных с сайта "Коммерсант"
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import feedparser
from datetime import datetime, timedelta
from ..config_schema import SectionsUrlRSS, NewsItem
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


def get_itemns(link_type: str, timedelta: datetime):
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
                body=None
            ))
    return News
def get_itemns_commersant():
    all_news = []
    for link in ag_conf_1.search_sections:
        news = get_itemns(getattr(cm_urls, link))
        all_news.append(news)
    #########
    # тут надо фильтрацию по эмитентам,
    # по названию и самой ссылке
    
    ########
    return all_news

def get_article_content(url: str) -> str:
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        #### поиск текста по тегам и классу
        article_text = soup.find_all('p', class_='doc__text')
        ### поиск текста по тегам и классу
        text = ""
        for part in article_text:
            text +=part.get_text(strip=True)
        return text
    except Exception as e:
        print(f"Ошибка при получении статьи {url}: {e}")
        return None
if __name__ == '__main__':
    # feed = feedparser.parse(cm_urls.main)
    # timedelta = datetime.now() - timedelta(hours=24)
    # for entry in feed.entries:
    #     published = datetime(*entry.published_parsed[:6])
    #     if published >= timedelta:
    #         print(f"{published:%Y-%m-%d %H:%M}")
    #         print(entry.title)
    #         print(entry.link)
    #         print(source)
    #         print(entry.description)
    #         print()
    
    get_article_content("https://www.kommersant.ru/doc/7799502")

