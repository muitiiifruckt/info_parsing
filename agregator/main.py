import time
from .connectors.ria import get_ria_news
from .connectors.russia_magazine import get_russia_magazine_news
from .connectors.rbk import get_rbk_news
from .connectors.tasss import get_tass_news
import os

SEEN_FILE = "seen_news.txt"

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for link in seen:
            f.write(link + "\n")

def run_all_parsers(hours: int = 24, seen=None):
    all_news = []
    all_news.extend(get_ria_news(hours))
    all_news.extend(get_russia_magazine_news(hours))
    all_news.extend(get_rbk_news(hours))
    all_news.extend(get_tass_news(hours))
    # Фильтруем только новые
    print()
    print(seen)
    print("Seen")
    print()
    if seen is not None:
        new_news = [item for item in all_news if item.link not in seen]
        return new_news
    return all_news

if __name__ == "__main__":
    period_minutes = 10  # Период проверки в минутах
    seen = load_seen()
    while True:
        news = run_all_parsers(hours=24, seen=seen)
        for item in news:
            print(item)
            seen.add(item.link)
        print(len(news))
        save_seen(seen)
        print(f"Проверка завершена, ждем {period_minutes} минут...\n")
        time.sleep(period_minutes * 60)