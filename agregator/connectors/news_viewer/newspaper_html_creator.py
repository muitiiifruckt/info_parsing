import re
from agregator.config_schema import NewsItem
import os
from datetime import date

NEWS_PATH = r"all_news.txt"
NEWS_HTML_DIR = r"agregator\connectors\news_viewer\html_papers"
def create_html():
    # --- 1. читаем файл ---
    # читаем и сохраняем содержимое
    with open(NEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # создаём временный пустой файл
    tmp_path = NEWS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        pass  # пустой

    # атомарно заменяем исходный файл
    os.replace(tmp_path, NEWS_PATH)

    # --- 2. разбиваем на блоки ---
    blocks = re.split(r"\n-{3,}\n", content)
    blocks = [b.strip() for b in blocks if b.strip()]

    news_list = []

    # --- 3. парсим каждую новость ---
    for block in blocks:
        title_match = re.search(r"^Название:\s*(.+)", block, re.MULTILINE)
        source_match = re.search(r"^Источник:\s*(.+)", block, re.MULTILINE)
        link_match = re.search(r"^Ссылка:\s*(.+)", block, re.MULTILINE)
        article_match = re.search(r"^Статья:\s*(.+)", block, re.DOTALL | re.MULTILINE)

        if title_match and source_match and link_match and article_match:
            news_list.append({
                "title": title_match.group(1).strip(),
                "source": source_match.group(1).strip(),
                "link": link_match.group(1).strip(),
                "article": article_match.group(1).strip()
            })

    # --- 4. формируем HTML ---
    html_header = """<!doctype html>
    <html lang="ru">
    <head>
    <meta charset="utf-8">
    <style>
    body { font-family: system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:#f2f2f2; padding:30px 0; }
    .news { width:80%; max-width:1200px; margin:0 auto; counter-reset: news-counter; }
    details { background:#fff; margin:18px 0; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.1); padding:20px 24px; counter-increment: news-counter; }
    summary::before { content: counter(news-counter) ". "; font-weight:700; color:#0078d7; }
    summary { cursor:pointer; font-size:1.2rem; font-weight:600; color:#0078d7; outline:none; }
    summary::-webkit-details-marker { display:none; }
    .article { margin-top:16px; font-size:1rem; line-height:1.6; color:#333; }
    .article a { display:inline-block; margin-top:10px; padding:8px 14px; background:#0078d7; color:#fff; text-decoration:none; border-radius:6px; font-size:0.9rem; }
    @media (max-width:600px){ .news {width:95%} }
    </style>
    </head>
    <body>
    <div class="news">
    """

    html_footer = "</div></body></html>"

    # --- 5. формируем блоки новостей ---
    html_news = ""
    for news in news_list:
        # заменяем переносы строк на <br>, чтобы не было проблем с f-string
        article_html = news['article'].replace('\n', '<br>')
        html_news += f"""
    <details>
    <summary>{news['title']}</summary>
    <div class="article">
    <p>{article_html}</p>
    <a href="{news['link']}" target="_blank">{news['source']}</a>
    </div>
    </details>
    """

    # формируем имя файла с текущей датой
    today = date.today().strftime("%Y-%m-%d")  # 2025-09-11
    filename = f"news_{today}.html"

    # полный путь к файлу
    file_path = os.path.join(NEWS_HTML_DIR, filename)

    # --- 6. сохраняем 
    # формируем имя файла с текущей датой
    today = date.today().strftime("%Y-%m-%d")  # 2025-09-11
    filename = f"news_{today}.html"

    # полный путь к файлу
    file_path = os.path.join(NEWS_HTML_DIR, filename)


    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_header + html_news + html_footer)
        
    print(f"Готово! {len(news_list)} новостей сохранено в news.html")
