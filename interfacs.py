from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

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
            # Открываем сайт
            page.goto("https://www.interfax.ru/")
            time.sleep(1)
            
            # Получаем HTML контент
            html_content = page.content()
            
            # Парсим HTML с помощью BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Находим блок с последними новостями
            timeline = soup.find('div', class_='timeline')
            if not timeline:
                print("Блок с последними новостями не найден")
                return
                
            # Находим все элементы с новостями
            news_items = timeline.find_all(['div'], class_=['timeline__text', 'timeline__text-large', 'timeline__photo', ''])
            
            print("\nПоследние новости:")
            print("-" * 80)
            
            # Обрабатываем каждую новость
            for item in news_items:
                try:
                    # Получаем время
                    time_elem = item.find('time')
                    news_time = time_elem.text if time_elem else "Время не указано"
                    
                    # Получаем ссылку и заголовок
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        news_link = link_elem.get('href', '')
                        # Если ссылка относительная, добавляем домен
                        if news_link.startswith('/'):
                            news_link = f"https://www.interfax.ru{news_link}"
                        
                        # Получаем заголовок
                        title_elem = link_elem.find('h3')
                        news_title = title_elem.text.strip() if title_elem else link_elem.get('title', 'Нет заголовка')
                        
                        # Выводим информацию
                        print(f"Время: {news_time}")
                        print(f"Заголовок: {news_title}")
                        print(f"Ссылка: {news_link}")
                        print("-" * 80)
                    
                except Exception as e:
                    print(f"Ошибка при обработке новости: {str(e)}")
                    continue
            
            # Ждем, пока пользователь закроет браузер
            input("\nНажмите Enter для закрытия браузера...")
            
        finally:
            browser.close()

if __name__ == '__main__':
    main()