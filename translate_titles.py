import os
from pathlib import Path
from googletrans import Translator

# Инициализируем переводчик (английский -> русский)
translator = Translator()

# Пути к папкам с контентом (относительно корня проекта)
BLOGS_DIR = Path("api/content/blogs")
PROJECTS_DIR = Path("api/content/projects")

def translate_file(filepath):
    print(f"Обработка: {filepath.name}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем, есть ли YAML front matter (начинается с ---)
        if not content.startswith('---'):
            print(f"  Пропущено: нет блока метаданных")
            return

        # Разделяем файл на метаданные и текст
        parts = content.split('---', 2)
        if len(parts) < 3:
            return

        front_matter = parts[1]
        body = parts[2]

        # Ищем строку с title
        new_front_matter = ""
        title_found = False
        
        for line in front_matter.strip().split('\n'):
            if line.strip().startswith('title:'):
                # Извлекаем текущий заголовок
                old_title = line.split(':', 1)[1].strip()
                if old_title:
                    # Переводим
                    translated = translator.translate(old_title, src='en', dest='ru').text
                    print(f"  {old_title} -> {translated}")
                    new_front_matter += f"title: {translated}\n"
                    title_found = True
                else:
                    new_front_matter += line + "\n"
            else:
                new_front_matter += line + "\n"

        # Собираем файл обратно
        if title_found:
            new_content = f"---\n{new_front_matter.strip()}\n---{body}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print(f"  Пропущено: поле title не найдено")

    except Exception as e:
        print(f"  Ошибка: {e}")

def main():
    print("--- Начинаем перевод заголовков ---")
    
    # Обрабатываем блоги
    if BLOGS_DIR.exists():
        print(f"\nПапка: {BLOGS_DIR}")
        for file in BLOGS_DIR.glob("*.md"):
            translate_file(file)

    # Обрабатываем проекты
    if PROJECTS_DIR.exists():
        print(f"\nПапка: {PROJECTS_DIR}")
        for file in PROJECTS_DIR.glob("*.md"):
            translate_file(file)
            
    print("\n--- Готово! ---")

if __name__ == "__main__":
    main()