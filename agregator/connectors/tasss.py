# agregator/connectors/tasss.py
from .rss_parser import parse_rss
from ..config import ag_conf_1 as config

def get_tass_news(emitents: list, search_within: bool):
    return parse_rss('https://tass.ru/rss/v2.xml', 'ТАСС', emitents, search_within)

if __name__ == '__main__':
    search_within = config.search_within
    emitents = config.emitent

    news = get_tass_news(emitents, search_within)
    print(news)
    print(len(news))