import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .connectors.ria import get_ria_news
from .connectors.russia_magazine import get_russia_magazine_news
from .connectors.rbk import get_rbk_news
from .connectors.tasss import get_tass_news
from .connectors.commersant_e import CommersantParser
from .connectors.Vedomosti import get_filtered_items as get_vedomosti_news
from .connectors.interfacs_e import main as interfacs_main
from .config import ag_conf_1 as config
from .config import commersant_params,interfax_params
from threading import Thread
from agregator.connectors.news_viewer.server import run_server
from agregator.connectors.news_viewer.newspaper_html_creator import create_html
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

def load_saved_links(filename="saved_links.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_link(link, filename="saved_links.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def save_news_to_txt(news_list, txt_filename="all_news.txt", links_filename="saved_links.txt"):
    saved_links = load_saved_links(links_filename)
    with open(txt_filename, "a", encoding="utf-8") as f:
        for item in news_list:
            if item.link in saved_links:
                continue  # Пропускаем уже сохранённые
            f.write(f"Название: {item.title}\n")
            f.write(f"Источник: {item.source}\n")
            f.write(f"Ссылка: {item.link}\n")
            f.write("Статья:\n")
            if item.body:
                f.write(item.body.strip() + "\n")
            f.write("\n---\n\n")
            save_link(item.link, links_filename)  # Добавляем ссылку в список сохранённых

def fetch_rss_news():
    emitents = config.emitent
    search_within = config.search_within
    news = []
    # РИА
    try:
        ria_news = get_ria_news(emitents, search_within)
        news += ria_news
        print(f"[РИА] Получено {len(ria_news)} новостей:")
        for item in ria_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO RIA", e)
    # Российская газета
    try:
        rg_news = get_russia_magazine_news(emitents, search_within)
        news += rg_news
        print(f"[Российская газета] Получено {len(rg_news)} новостей:")
        for item in rg_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO RG", e)
    # РБК
    try:
        rbk_news = get_rbk_news(emitents, search_within)
        news += rbk_news
        print(f"[РБК] Получено {len(rbk_news)} новостей:")
        for item in rbk_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO RBK", e)
    # ТАСС
    try:
        tass_news = get_tass_news(emitents, search_within)
        news += tass_news
        print(f"[ТАСС] Получено {len(tass_news)} новостей:")
        for item in tass_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO TASS", e)
    print(f"[{datetime.now()}] Всего получено {len(news)} новостей (RSS)")
    save_news_to_txt(news)

def fetch_daily_news():
    emitents = config.emitent
    search_within = config.search_within
    news = []
    # Коммерсант
    try:
        commersant_news = CommersantParser(commersant_params)
        news += commersant_news
        print(f"[Коммерсант] Получено {len(commersant_news)} новостей:")
        for item in commersant_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO Kommersant", e)
    # Ведомости
    try:
        vedomosti_news = get_vedomosti_news(config)
        news += vedomosti_news
        print(f"[Ведомости] Получено {len(vedomosti_news)} новостей:")
        for item in vedomosti_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO Vedomosti", e)
    # Интерфакс
    try:
        interfacs_news = interfacs_main()
        news += interfacs_news
        print(f"[Интерфакс] Получено {len(interfacs_news)} новостей:")
        for item in interfacs_news:
            print(f"  - {item.link}")
    except Exception as e:
        print("NO Interfacs", e)
    print(f"[{datetime.now()}] Всего получено {len(news)} новостей (daily)")
    save_news_to_txt(news)
    # ОЧИСТКА ФАЙЛА ПОСЛЕ СОХРАНЕНИЯ
    with open("all_news.txt", "w", encoding="utf-8") as f:
        pass  # Просто очищаем файл

if __name__ == "__main__":
    # запускаем Flask-сервер в отдельном потоке
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Даем серверу время на запуск
    import time
    time.sleep(2)
    
    # запускаем планировщик
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")
    scheduler.add_job(fetch_rss_news, 'interval', minutes=15, id='rss_news')
    scheduler.add_job(fetch_daily_news, 'cron', hour=23, minute=59, id='daily_news')
    scheduler.add_job(create_html, 'cron', hour=23, minute=59, id='html_creator')
    
    scheduler.start()
    
    print("Сбор новостей запущен. Сервер работает в фоне. Для остановки нажмите Ctrl+C.")
    
    try:
        # Бесконечный цикл вместо блокирующего scheduler
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Остановка парсера.")
        scheduler.shutdown()