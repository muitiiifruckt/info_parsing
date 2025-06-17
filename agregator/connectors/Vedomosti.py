import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_today_vedomosti_news():
    url = "https://www.vedomosti.ru/news"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    news_items = []
    today = datetime.now().date()

    for article in soup.select('div.card-news'):  # структура может меняться, см. HTML

        link_tag = article.find('a', href=True)
 
        date_tag = article.select_one('.card-news__date')
        
        if not link_tag or not date_tag:
            continue

        # Пример даты: "10 июня, 11:45"
        date_text = date_tag.text.strip()
        try:
            match = re.search(r"(\d{1,2}) (\w+)", date_text)
            if match:
                day, month_name = match.groups()
                months = {
                    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5,
                    'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9,
                    'октября': 10, 'ноября': 11, 'декабря': 12
                }
                pub_date = datetime(datetime.now().year, months[month_name], int(day)).date()
            else:
                continue
        except Exception:
            continue

        if pub_date == today:
            news_items.append({
                "title": link_tag.get_text(strip=True),
                "link": "https://www.vedomosti.ru" + link_tag["href"]
            })

    return news_items
if __name__ == "__main__":
    news = get_today_vedomosti_news()
    for n in news:
        print(n["title"], "-", n["link"])
