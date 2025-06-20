# agregator/main.py
import time
from .connectors.ria import get_ria_news
from .connectors.russia_magazine import get_russia_magazine_news
from .connectors.rbk import get_rbk_news
from .connectors.tasss import get_tass_news

def run_all_parsers(hours: int = 1):
    all_news = []
    all_news.extend(get_ria_news(hours))
    print(all_news)
    all_news.extend(get_russia_magazine_news(hours))
    all_news.extend(get_rbk_news(hours))
    all_news.extend(get_tass_news(hours))
    return all_news

if __name__ == "__main__":
    period_minutes = 10  # Период проверки в минутах
    while True:
        news = run_all_parsers(hours=24)
        for item in news:
            print(item)
        print(len(news))
        print(f"Проверка завершена, ждем {period_minutes} минут...\n")
        time.sleep(period_minutes * 60)