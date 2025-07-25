from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from datetime import date, timedelta,datetime
from agregator.config_schema import NewsItem, src_prms  # Импортируйте общий NewsItem
from ..config import ag_conf_1 as config
from .rss_parser import save_news_to_txt
import logging


class NewsParser:
    def __init__(self, params : src_prms):
        self.news_set: set[NewsItem] = set()
        self.params = params
        
    def get_soup(self, html_content) -> str:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except:
            logging.error(f"Не получись получить soup -")
        return soup
    
    def get_news_items(self,soup:str) -> List[str]:
        try:
            news_items = soup.find('div', class_= self.params.res_news_cls)
            news_items = news_items.find_all("div",recursive =False)
        except:
            logging.error(f"Ошибка при попытке извлечь список статей")
            
        return news_items
        
    def get_item_time(self, item:str) ->str | None: 
        try:
            time_elem = item.find('time')
            news_time = time_elem.text.strip() if time_elem else None
        except:
            logging.error(f"Ошибка при попытке извлечь список статей")
            
        return news_time
    def get_item_title(self, item:str) -> str:
        pass
    def get_item_link(self, item:str) -> str:
        pass
    def get_item_body(self, item:str) -> str:
        pass
    def get_item_description(self, item:str) -> str:
        pass
        
    def parse_news(self, html_content: str, company: str, page=None) -> set[NewsItem]:
        """Парсит HTML и извлекает новости"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Находим все новости в результатах поиска
            news_items = soup.find('div', class_= self.params.res_news_cls)
            news_items = news_items.find_all("div",recursive =False)
            
            
            for item in news_items:
                try:
                    # Дата
                    time_elem = item.find('time')
                    news_time = time_elem.text.strip() if time_elem else None

                    # Для блока с фото ищем внутри .title
                    if 'sPageResult__photo' in item.get('class', []):
                        title_div = item.find('div', class_='title')
                        links = title_div.find_all('a') if title_div else []
                    else:
                        links = item.find_all('a')

                    if len(links) > 1:
                        news_link = links[1].get('href', '')
                        news_title = links[1].text.strip()
                        if news_link.startswith('/'):
                            news_link = f"https://www.interfax.ru{news_link}"
                    else:
                        news_link = None
                        news_title = None

                    print(f"Дата: {news_time}")
                    print(f"Заголовок: {news_title}")
                    print(f"Ссылка: {news_link}")
                    record = self.get_article_text(page, news_link) if page and news_link else None
                    print(f"Статья - {record}")
                    print('-' * 40)
                    
                    
                    # Проверка на уникальность по ссылке
                    if news_link in self.seen_links:
                        print("Повторение статьи")
                        print()
                        continue  # уже добавляли такую новость

                    # Создаем объект новости
                    news_item = NewsItem(
                    time=news_time,
                    title=news_title,
                    link=news_link,
                    source="interfax.ru",
                    description=None,  # если есть краткое описание, иначе None
                    emitent=self.company,        # если компания — эмитент
                    body=record             # полный текст статьи, если парсите
                    )
                    self.news_list.append(news_item)
                    self.seen_links.add(news_link)  # добавляем ссылку в множество
                    
                except Exception as e:
                    print(f"Ошибка при обработке новости: {str(e)}")
                    continue
        except:
            pass
        return self.news_list

    def get_article_text(self, page, url):
        page.goto(url)
        page.wait_for_load_state('networkidle')
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = '\n'.join(p.get_text() for p in paragraphs if p.get_text(strip=True))
        return article_text
    
    def print_news(self):
        """Выводит новости в консоль"""
        print("\nНайденные новости:")
        print("-" * 80)
        
        for news in self.news_list:
            print(f"Компания: {news.emitent}")
            print(f"Время: {news.time}")
            print(f"Заголовок: {news.title}")
            print(f"Ссылка: {news.link}")
            
            print("-" * 80)

def main():
    timedelta_dt = 24
    search_within = config.search_within # True поиск идет по поискавику интерфакса
    emitents = config.emitent
    link_types = config.search_sections
    
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
            for company in emitents:
                print(f"\nПоиск новостей о компании: {emitents}")
                
                # Открываем страницу поиска
                page.goto("https://www.interfax.ru/search/")
                time.sleep(1)
                
                # Находим форму поиска и вводим название компании
                search_form = page.locator('.sPageForm')
                search_input = page.locator('input[name="phrase"]')
                # Используем более специфичный селектор для поля ввода в основной форме поиска
                search_input = page.locator('main input[name="phrase"]')
                
                search_input.fill(company)
                # Установить дату "20.06.2024" в поле с id="from"
                offset = date.today() - timedelta(hours=timedelta_dt)
                date_str = offset.strftime('%d.%m.%Y')
                #date_str = "28.06.2025"
                page.fill('input#from', date_str)
                
                # Отправляем форму
                search_form.evaluate('form => form.submit()')
                time.sleep(2)  # Ждем загрузки результатов
                
                # Получаем HTML контент
                html_content = page.content()
                
                # Парсим результаты
                parser.parse_news(html_content, company, page=page)
                
                # Небольшая задержка между запросами
                time.sleep(1)
            
            # Выводим все найденные новости
            parser.print_news()
            return parser.news_list
            
            # Ждем, пока пользователь закроет браузер
            input("\nНажмите Enter для закрытия браузера...")
            
        finally:
            browser.close()

if __name__ == '__main__':
    news = main()
    save_news_to_txt(news)