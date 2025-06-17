from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

# Список источников для поиска (пример, замените на ваш список)
SOURCES = ['Газпром', 'Сбербанк', 'Лукойл']
@dataclass
class NewsItem:
    time: str
    title: str
    link: str
    source: str
    has_image: bool = False

class VedomostiParser:
    def __init__(self):
        self.news_list: List[NewsItem] = []

    def parse_news(self, html_content: str, source: str) -> List[NewsItem]:
        soup = BeautifulSoup(html_content, 'html.parser')
        news_items = soup.find_all('a', class_='search-item search-page__article')
        for item in news_items:
            try:
                news_link = item.get('href', '')
                if news_link.startswith('/'):
                    news_link = f"https://www.vedomosti.ru{news_link}"
                news_title = item.find('h4', class_='search-item__title')
                news_title = news_title.text.strip() if news_title else ''
                news_time = item.find('span', class_='search-item__date')
                news_time = news_time.text.strip() if news_time else ''
                has_image = bool(item.find('img'))
                self.news_list.append(NewsItem(
                    time=news_time,
                    title=news_title,
                    link=news_link,
                    source=source,
                    has_image=has_image
                ))
            except Exception as e:
                print(f"Ошибка: {e}")
        return self.news_list

    def print_news(self):
        print("\nНайденные новости:")
        print("-" * 80)
        for news in self.news_list:
            print(f"Источник: {news.source}")
            print(f"Время: {news.time}")
            print(f"Заголовок: {news.title}")
            print(f"Ссылка: {news.link}")
            if news.has_image:
                print("📷 Есть изображение")
            print("-" * 80)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        parser = VedomostiParser()
        try:
            for source in SOURCES:
                print(f"\nПоиск по: {source}")
                page.goto(f"https://www.vedomosti.ru/search?query={source}")
                time.sleep(2)
                try:
                    # Пример: ищем кнопку закрытия по CSS-селектору (уточните селектор под вашу рекламу)
                    close_btn = page.query_selector('button[aria-label="Закрыть"], .close, .popup__close, .modal__close')
                    if close_btn:
                        close_btn.click()
                        time.sleep(1)  # Дать странице обновиться
                except Exception as e:
                    print("Не удалось закрыть рекламу:", e)
                html_content = page.content()
                parser.parse_news(html_content, source)
                time.sleep(1)
            parser.print_news()
            input("\nНажмите Enter для закрытия браузера...")
        finally:
            browser.close()

if __name__ == '__main__':
    main()
