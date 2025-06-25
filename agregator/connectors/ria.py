# agregator/connectors/ria.py
from .rss_parser import parse_rss
from ..config import ag_conf_1 as config

def get_ria_news(emitents: list, search_within: bool):
    return parse_rss('https://ria.ru/export/rss2/index.xml', 'РИА Новости', emitents, search_within)

if __name__ == '__main__':
    search_within = config.search_within
    emitents = config.emitent

    news = get_ria_news(emitents, search_within)
    print(news)
    print(len(news))