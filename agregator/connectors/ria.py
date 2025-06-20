# agregator/connectors/ria.py
from .rss_parser import parse_rss

def get_ria_news(hours: int = 1):
    return parse_rss('https://ria.ru/export/rss2/index.xml', 'РИА Новости', hours)