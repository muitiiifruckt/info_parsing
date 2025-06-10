from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional

# Список компаний для поиска
COMPANIES = ['Газпром', 'Сбербанк', 'Лукойл']

@dataclass
class NewsItem:
    """Класс для хранения информации о новости"""
    time: str
    title: str
    link: str
    company: str
    has_image: bool = False

class NewsParser:
    def __init__(self):
        self.news_list: List[NewsItem] = []
        
    def parse_news(self, html_content: str, company: str) -> List[NewsItem]:
        """Парсит HTML и извлекает новости"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Находим все новости в результатах поиска
        news_items = soup.find_all('div', class_='sPageResult')
        
        for item in news_items:
            try:
                print(item)
                print()
                # Получаем время
                time_elem = item.find('time')
                if not time_elem:
                    continue
                    
                news_time = time_elem.text
                
                # Получаем ссылку и заголовок
                link_elem = item.find('a', class_='sPageResult__link')
                if not link_elem:
                    continue
                    
                news_link = link_elem.get('href', '')
                if news_link.startswith('/'):
                    news_link = f"https://www.interfax.ru{news_link}"
                
                news_title = link_elem.text.strip()
                
                # Проверяем наличие изображения
                has_image = bool(item.find('img'))
                
                # Создаем объект новости
                news_item = NewsItem(
                    time=news_time,
                    title=news_title,
                    link=news_link,
                    company=company,
                    has_image=has_image
                )
                
                self.news_list.append(news_item)
                
            except Exception as e:
                print(f"Ошибка при обработке новости: {str(e)}")
                continue
                
        return self.news_list
    
    def print_news(self):
        """Выводит новости в консоль"""
        print("\nНайденные новости:")
        print("-" * 80)
        
        for news in self.news_list:
            print(f"Компания: {news.company}")
            print(f"Время: {news.time}")
            print(f"Заголовок: {news.title}")
            print(f"Ссылка: {news.link}")
            if news.has_image:
                print("📷 Новость содержит изображение")
            print("-" * 80)

def main():
    with sync_playwright() as p:
        # Запуск браузера в видимом режиме
        browser = p.chromium.launch(headless=False)
        
        # Создание нового контекста
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Создание новой страницы
        page = context.new_page()
        
        try:
            # Создаем парсер
            parser = NewsParser()
            
            # Для каждой компании выполняем поиск
            for company in COMPANIES:
                print(f"\nПоиск новостей о компании: {company}")
                
                # Открываем страницу поиска
                page.goto("https://www.interfax.ru/search/")
                time.sleep(1)
                
                # Находим форму поиска и вводим название компании
                search_form = page.locator('.sPageForm')
                search_input = page.locator('input[name="phrase"]')
                # Используем более специфичный селектор для поля ввода в основной форме поиска
                search_input = page.locator('main input[name="phrase"]')
                search_input.fill(company)
                
                # Отправляем форму
                search_form.evaluate('form => form.submit()')
                time.sleep(2)  # Ждем загрузки результатов
                
                # Получаем HTML контент
                html_content = page.content()
                
                # Парсим результаты
                parser.parse_news(html_content, company)
                
                # Небольшая задержка между запросами
                time.sleep(1)
            
            # Выводим все найденные новости
            parser.print_news()
            
            # Ждем, пока пользователь закроет браузер
            input("\nНажмите Enter для закрытия браузера...")
            
        finally:
            browser.close()

if __name__ == '__main__':
    main()
