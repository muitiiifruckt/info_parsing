from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import time

@dataclass
class CbondsNewsItem:
    title: str
    link: str
    date: str

def parse_cbonds_news(html: str) -> List[CbondsNewsItem]:
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []
    
    # На странице новостей Cbonds новости находятся в блоках с классом "news-item" (пример, может отличаться)
    news_blocks = soup.select('div.news-item')  # Нужно уточнить селектор по сайту
    
    for block in news_blocks:
        # Заголовок
        a_tag = block.find('a')
        if not a_tag:
            continue
        title = a_tag.text.strip()
        
        # Ссылка
        link = a_tag.get('href')
        if link and link.startswith('/'):
            link = 'https://cbonds.com' + link
        
        # Дата — обычно в каком-то span или div, попробуем найти
        date_tag = block.find('div', class_='date') or block.find('span', class_='date')
        date = date_tag.text.strip() if date_tag else ''
        
        news_items.append(CbondsNewsItem(title=title, link=link, date=date))
    return news_items

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # URL с новостями (пример - надо взять реальный раздел новостей)
        url = 'https://cbonds.com/news'
        
        page.goto(url)
        time.sleep(2)  # ждем загрузки
        
        html = page.content()
        news = parse_cbonds_news(html)
        
        for item in news:
            print(f"{item.date} - {item.title}")
            print(f"→ {item.link}\n")
        
        browser.close()

if __name__ == '__main__':
    main()
