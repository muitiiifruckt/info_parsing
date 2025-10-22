from flask import Flask, send_file, abort, render_template_string, request, jsonify
import os, glob, json

app = Flask(__name__)

# 🔹 Папка с HTML-новостями относительно этого скрипта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BASE_DIR, "html_papers")  # html_papers рядом со server.py
LABELS_FILE = os.path.join(NEWS_DIR, "labels.jsonl")
# создаём папку, если её нет
os.makedirs(NEWS_DIR, exist_ok=True)
print("Папка новостей:", NEWS_DIR)

@app.post("/label")
def save_label():
    data = request.get_json(silent=True) or {}
    link = data.get('link')
    
    if not link:
        return jsonify(ok=False, error="No link provided")
    
    # Читаем существующие записи
    existing_records = []
    if os.path.exists(LABELS_FILE):
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line.strip())
                        existing_records.append(record)
                    except json.JSONDecodeError:
                        continue
    
    # Проверяем, есть ли уже запись с такой ссылкой
    existing_index = None
    for i, record in enumerate(existing_records):
        if record.get('link') == link:
            existing_index = i
            break
    
    if existing_index is not None:
        # Удаляем существующую запись
        del existing_records[existing_index]
    else:
        # Добавляем новую запись
        existing_records.append(data)
    
    # Перезаписываем файл
    with open(LABELS_FILE, "w", encoding="utf-8") as f:
        for record in existing_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    return jsonify(ok=True)

@app.route("/news")
def news_index():
    # ищем все html-файлы
    files = glob.glob(os.path.join(NEWS_DIR, "*.html"))
    print("Нашли файлы:", files)  # отладка в терминале

    # извлекаем имена файлов без расширения
    versions = [os.path.splitext(os.path.basename(f))[0] for f in sorted(files, reverse=True)]

    # формируем HTML со ссылками
    html = render_template_string("""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Сводки новостей</title>
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        color: #333;
        margin: 0;
        padding: 0;
    }
    .container {
        max-width: 800px;
        margin: 50px auto;
        padding: 20px;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    h1 {
        text-align: center;
        color: #222;
    }
    ul {
        list-style: none;
        padding: 0;
    }
    li {
        margin: 10px 0;
    }
    a {
        display: block;
        padding: 12px 20px;
        text-decoration: none;
        color: #fff;
        background-color: #007bff;
        border-radius: 6px;
        transition: background-color 0.2s;
    }
    a:hover {
        background-color: #0056b3;
    }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Сводки новостей</h1>
        <ul>
        {% for v in versions %}
            <li><a href="/news/{{v}}">{{v}}</a></li>
        {% endfor %}
        </ul>
    </div>
    </body>
    </html>

    """, versions=versions)
    return html

@app.route("/news/<name>")
def get_news_by_name(name):
    filename = os.path.join(NEWS_DIR, f"{name}.html")
    print("Пробуем открыть:", filename)
    if os.path.exists(filename):
        return send_file(filename, mimetype="text/html")
    else:
        abort(404, description="Новости не найдены")
        
def run_server():
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)

if __name__ == "__main__":
    print("Открой в браузере: http://127.0.0.1:8000/news")
    app.run(host="0.0.0.0", port=8000, debug=True)
