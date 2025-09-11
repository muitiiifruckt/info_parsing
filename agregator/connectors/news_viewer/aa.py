import os, glob

# укажи сюда реальный абсолютный путь к папке, где лежат html-файлы
NEWS_DIR = r"C:\Users\aayza\OneDrive\Документы\info_parsing\agregator\connectors\news_viewer\html_papers"

print("Проверяем папку:", NEWS_DIR)

if not os.path.exists(NEWS_DIR):
    print("❌ Папка не существует")
else:
    files = glob.glob(os.path.join(NEWS_DIR, "*.html"))
    if not files:
        print("⚠️ Файлы .html не найдены")
    else:
        print("✅ Найдены файлы:")
        for f in files:
            print(" -", f)
