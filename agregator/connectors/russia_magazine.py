# agregator/connectors/russia_magazine.py
from .rss_parser import parse_rss

def get_russia_magazine_news(hours: int = 1):
    return parse_rss('https://rg.ru/xml/index.xml', 'Российская газета', hours)