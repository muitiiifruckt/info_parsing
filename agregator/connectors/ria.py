import feedparser

# URL RSS-ленты РИА Новости
RSS_URL = "https://ria.ru/export/rss2/index.xml"

def fetch_ria_news():
    feed = feedparser.parse(RSS_URL)

    print(f"Заголовок ленты: {feed.feed.title}")
    print(f"Описание: {feed.feed.get('description', 'Нет описания')}")
    print("\nПоследние новости:\n")

    for entry in feed.entries[:10]:  # Покажем 10 последних новостей
        print(f"- {entry.title}")
        print(f"  📅 {entry.published}")
        print(f"  🔗 {entry.link}")
        print()

if __name__ == "__main__":
    fetch_ria_news()
