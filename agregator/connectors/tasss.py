# agregator/connectors/tasss.py
from .rss_parser import parse_rss

def get_tass_news(hours: int = 1):
    return parse_rss('https://tass.ru/rss/v2.xml', 'ТАСС', hours)