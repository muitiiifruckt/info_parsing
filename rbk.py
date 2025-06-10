import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Компании для мониторинга
COMPANIES = ['Газпром', 'Сбербанк', 'Лукойл']

# URL раздела "Бизнес"
URL_1 = 'https://www.rbc.ru/business/'
URL_2 = 'https://www.rbc.ru/politics/'
URL_3 = 'https://www.rbc.ru/economics/' 
URL_4 = 'https://www.rbc.ru/technology_and_media/'
URL_5 = 'https://www.rbc.ru/finances/'

# Заголовки User-Agent для обхода простейших защит
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def get_articles():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    i = 0
    # Обработка карточек новостей
    for tag in soup.select('div.item.js-rm-central-column-item.item_image-mob.js-category-item'):
        i += 1
        print(i)
        #print(tag)
        title_tag = tag.find('span', class_='no-wrap')
        link_tag = tag.find(class_='item__link rm-cm-item-link js-rm-central-column-item-link').get('href')
        time_tag = tag.find('span', class_='item__category')

        print(title_tag.text)
        
        print(link_tag)
        print()
        if not (title_tag and link_tag):
            continue

        # title = title_tag.get_text(strip=True)
        # link = link_tag['href']
        
        # time_str = time_tag.get_text(strip=True) if time_tag else "Не указано"

        # # Проверка на наличие нужной компании
        # if any(company.lower() in title.lower() for company in COMPANIES):
        #     articles.append({
        #         'title': title,
        #         'link': link,
        #         'time': time_str
        #     })

    return articles


if __name__ == "__main__":
    news = get_articles()

    if not news:
        print("Ничего не найдено.")
    else:
        for item in news:
            print(f"📰 {item['title']}")
            print(f"⏱️ {item['time']}")
            print(f"🔗 {item['link']}")
            print('-' * 50)
