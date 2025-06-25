# agregator/connectors/rbk.py
from .rss_parser import parse_rss

def get_rbk_news(hours: int = 1):
    return parse_rss('https://rssexport.rbc.ru/rbcnews/news/30/full.rss', 'РБК', hours)


if __name__ == '__main__':
    print(get_rbk_news())