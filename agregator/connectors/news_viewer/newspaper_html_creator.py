import re
from agregator.config_schema import NewsItem
import os
from datetime import date
import html
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
        emitent_match = re.search(r"^Эмитент:\s*(.+)", block, re.MULTILINE)  # Добавить
        link_match = re.search(r"^Ссылка:\s*(.+)", block, re.MULTILINE)
        article_match = re.search(r"^Статья:\s*(.+)", block, re.DOTALL | re.MULTILINE)

        if title_match and source_match and link_match and article_match:
            news_list.append({
                "title": title_match.group(1).strip(),
                "source": source_match.group(1).strip(),
                "emitent": emitent_match.group(1).strip() if emitent_match else "Не указан",  # Добавить
                "link": link_match.group(1).strip(),
                "article": article_match.group(1).strip()
            })

    # --- 4. формируем HTML с фильтрами ---
    # Получаем уникальные источники и эмитенты
    sources = list(set(news['source'] for news in news_list))
    emitents = list(set(news['emitent'] for news in news_list))
    
    html_header = """<!doctype html>
    <html lang="ru">
    <head>
    <meta charset="utf-8">
    <style>
    body { font-family: system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:#f2f2f2; padding:30px 0; }
    .filters { width:80%; max-width:1200px; margin:0 auto 20px; background:#fff; padding:20px; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.1); }
    .filter-section { margin-bottom:15px; }
    .filter-section h3 { margin:0 0 10px; color:#333; font-size:1rem; }
    .filter-buttons { display:flex; flex-wrap:wrap; gap:8px; }
    .filter-btn { padding:6px 12px; border:1px solid #ddd; background:#f8f9fa; border-radius:4px; cursor:pointer; font-size:0.9rem; transition:all 0.2s; }
    .filter-btn.active { background:#0078d7; color:#fff; border-color:#0078d7; }
    .filter-btn:hover { background:#e9ecef; }
    .filter-btn.active:hover { background:#005a9e; }
    .news { width:80%; max-width:1200px; margin:0 auto; counter-reset: news-counter; }
    details { background:#fff; margin:18px 0; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.1); padding:20px 24px; counter-increment: news-counter; }
    summary::before { content: counter(news-counter) ". "; font-weight:700; color:#0078d7; }
    summary { cursor:pointer; font-size:1.2rem; font-weight:600; color:#0078d7; outline:none; display:flex; align-items:center; justify-content:space-between; gap:12px; }
    summary::-webkit-details-marker { display:none; }
    .article { margin-top:16px; font-size:1rem; line-height:1.6; color:#333; }
    .article a { display:inline-block; margin-top:10px; padding:8px 14px; background:#0078d7; color:#fff; text-decoration:none; border-radius:6px; font-size:0.9rem; }
    .actions { margin-top:12px; display:flex; gap:8px; }
    .ok { padding:8px 10px; border:0; border-radius:6px; cursor:pointer; font-size:0.9rem; transition: background-color .15s ease; background:#9ca3af; color:#fff; }
    .ok.active { background:#16a34a; color:#fff; }
    .news-item { display:none; }
    .news-item.visible { display:block; }
    @media (max-width:600px){ .news {width:95%} }
    </style>
    <script>
    function keyFor(link){ return "relabeled::" + link; }

    function applyInitialState(){
    document.querySelectorAll('button.ok[data-link]').forEach(btn => {
        const link = btn.getAttribute('data-link');
        if (localStorage.getItem(keyFor(link)) === '1') {
        btn.classList.add('active');
        }
    });
    }

        async function sendLabel(link, title, label) {
    try {
        await fetch('/label', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ link, title, label, ts: new Date().toISOString() })
        });
    } catch(e) { console.error(e); }
    }

    function toggleRelevant(ev, btn, link, title){
    ev.stopPropagation();
    ev.preventDefault();
    if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        localStorage.removeItem(keyFor(link));
        sendLabel(link, title, 'irrelevant');
    } else {
        btn.classList.add('active');
        localStorage.setItem(keyFor(link), '1');
        sendLabel(link, title, 'relevant');
    }
    }

    // Функции для фильтрации
    let activeFilters = {
        sources: new Set(),
        emitents: new Set()
    };

    function toggleFilter(type, value, button) {
        if (activeFilters[type].has(value)) {
            activeFilters[type].delete(value);
            button.classList.remove('active');
        } else {
            activeFilters[type].add(value);
            button.classList.add('active');
        }
        applyFilters();
    }

    function applyFilters() {
        const newsItems = document.querySelectorAll('.news-item');
        
        newsItems.forEach(item => {
            const source = item.getAttribute('data-source');
            const emitent = item.getAttribute('data-emitent');
            
            let show = true;
            
            // Если есть активные фильтры источников
            if (activeFilters.sources.size > 0 && !activeFilters.sources.has(source)) {
                show = false;
            }
            
            // Если есть активные фильтры эмитентов
            if (activeFilters.emitents.size > 0 && !activeFilters.emitents.has(emitent)) {
                show = false;
            }
            
            if (show) {
                item.classList.add('visible');
            } else {
                item.classList.remove('visible');
            }
        });
        
        // Обновляем счетчик видимых новостей
        const visibleCount = document.querySelectorAll('.news-item.visible').length;
        document.getElementById('news-count').textContent = visibleCount;
    }

    document.addEventListener('DOMContentLoaded', applyInitialState);
    </script>
    </head>
    <body>
    <div class="filters">
        <div class="filter-section">
            <h3>Источники:</h3>
            <div class="filter-buttons">
    """

    # Добавляем кнопки фильтров для источников
    for source in sources:
        safe_source = html.escape(source)
        html_header += f'<button class="filter-btn" onclick="toggleFilter(\'sources\', \'{safe_source}\', this)">{safe_source}</button>\n'
    
    html_header += """
            </div>
        </div>
        <div class="filter-section">
            <h3>Эмитенты:</h3>
            <div class="filter-buttons">
    """
    
    # Добавляем кнопки фильтров для эмитентов
    for emitent in emitents:
        safe_emitent = html.escape(emitent)
        html_header += f'<button class="filter-btn" onclick="toggleFilter(\'emitents\', \'{safe_emitent}\', this)">{safe_emitent}</button>\n'
    
    html_header += f"""
            </div>
        </div>
        <div style="margin-top:10px; font-size:0.9rem; color:#666;">
            Показано: <span id="news-count">{len(news_list)}</span> из {len(news_list)} новостей
        </div>
    </div>
    <div class="news">
    """

    html_footer = "</div></body></html>"
    
    # --- 5. формируем блоки новостей с атрибутами для фильтрации ---
    html_news = ""
    for news in news_list:
        article_html = news['article'].replace('\n', '<br>')
        safe_title = html.escape(news['title'])
        safe_link = html.escape(news['link'])
        safe_source = html.escape(news['source'])
        safe_emitent = html.escape(news['emitent'])
        
        html_news += f"""
        <details class="news-item visible" data-source="{safe_source}" data-emitent="{safe_emitent}">
        <summary><span class="sum-title">{safe_title}</span>
            <button class="ok" data-link="{safe_link}" data-title="{safe_title}" onclick="toggleRelevant(event,this,'{safe_link}','{safe_title}')">Релевантно</button>
        </summary>
        <div class="article">
            <p>{article_html}</p>
            <a href="{safe_link}" target="_blank">{news['source']}</a>
            <div style="margin-top:8px; font-size:0.85rem; color:#666;">
                Эмитент: {news['emitent']}
            </div>
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
