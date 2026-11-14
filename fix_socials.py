import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. Правим config.ini
config_path = BASE_DIR / "api" / "config.ini"
if config_path.exists():
    text = config_path.read_text(encoding="utf-8")
    # Заменяем linkedin на telegram
    text = re.sub(r'linkedin\s*=\s*.*', 'telegram = https://t.me/ваш_ник', text)
    # Добавляем vk перед twitter
    text = text.replace("twitter =", "vk = https://vk.com/ваш_ник\ntwitter =")
    config_path.write_text(text, encoding="utf-8")
    print("✅ config.ini обновлен")

# 2. Правим index.py
index_path = BASE_DIR / "api" / "index.py"
if index_path.exists():
    text = index_path.read_text(encoding="utf-8")
    # Меняем список ключей
    text = text.replace('"hubspot", "linkedin", "twitter",', '"hubspot", "telegram", "vk", "twitter",')
    index_path.write_text(text, encoding="utf-8")
    print("✅ index.py обновлен")

# 3. Правим home.html
html_path = BASE_DIR / "api" / "templates" / "home.html"
if html_path.exists():
    text = html_path.read_text(encoding="utf-8")
    
    # Ищем блок с LinkedIn и заменяем его на Telegram + VK
    pattern = re.compile(r'<a[^>]*href="\{\{\s*linkedin\s*\}\}"[^>]*>.*?</a>', re.DOTALL)
    
    new_buttons = '''<a class="btn btn-primary bg-dark mx-1 text-light mt-2 border border-secondary" href="{{ telegram }}" target="_blank" rel="noopener noreferrer">
    <span class="fa fa-telegram"></span>
  </a>
  <a class="btn btn-primary bg-dark mx-1 text-light mt-2 border border-secondary" href="{{ vk }}" target="_blank" rel="noopener noreferrer">
    <span class="fa fa-vk"></span>
  </a>'''
    
    if pattern.search(text):
        text = pattern.sub(new_buttons, text)
        html_path.write_text(text, encoding="utf-8")
        print("✅ home.html обновлен (LinkedIn заменен на Telegram и VK)")
    else:
        print("⚠️ В home.html не найден блок с LinkedIn. Возможно, он уже изменен.")

print("\n🚀 Готово! Не забудьте вписать реальные ссылки в config.ini и перезапустить службу.")