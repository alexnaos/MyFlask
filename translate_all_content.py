import os
from pathlib import Path
from googletrans import Translator
import time

# Инициализируем переводчик
translator = Translator()

# Указываем папку, которую нужно обработать
CONTENT_DIR = Path("api/content")

def translate_markdown_file(filepath):
    print(f"\nОбработка: {filepath.name}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return

        # Разделяем на Front Matter (метаданные) и Основной текст
        front_matter = ""
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                body = parts[2]

        # 1. Переводим Front Matter (только значения, ключи оставляем на английском)
        new_front_matter = ""
        if front_matter:
            for line in front_matter.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value and key not in ['date', 'published', 'publish']: # Дату и статус не переводим
                        try:
                            translated_val = translator.translate(value, src='en', dest='ru').text
                            new_front_matter += f"{key}: {translated_val}\n"
                            time.sleep(0.5) # Пауза, чтобы Google не забанил
                        except:
                            new_front_matter += line + "\n"
                    else:
                        new_front_matter += line + "\n"
                else:
                    new_front_matter += line + "\n"

        # 2. Переводим основной текст
        print("  Перевод основного текста...")
        # Разбиваем текст на абзацы, чтобы не превышать лимит символов Google
        paragraphs = body.split('\n\n')
        translated_paragraphs = []
        
        for p in paragraphs:
            if not p.strip():
                translated_paragraphs.append(p)
                continue
                
            # Не переводим блоки кода
            if p.strip().startswith('```'):
                translated_paragraphs.append(p)
                continue

            try:
                translated_p = translator.translate(p, src='en', dest='ru').text
                translated_paragraphs.append(translated_p)
                time.sleep(0.5) # Задержка между запросами
            except Exception as e:
                print(f"  Ошибка перевода абзаца: {e}")
                translated_paragraphs.append(p) # Оставляем оригинал при ошибке

        new_body = '\n\n'.join(translated_paragraphs)

        # Собираем файл обратно
        if front_matter:
            final_content = f"---\n{new_front_matter.strip()}\n---\n\n{new_body}"
        else:
            final_content = new_body

        # Записываем результат
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        print(f"  Успешно переведено!")

    except Exception as e:
        print(f"  Ошибка при обработке файла: {e}")

def main():
    print(f"--- Начинаем перевод всех .md файлов в {CONTENT_DIR} ---")
    if not CONTENT_DIR.exists():
        print(f"Ошибка: Папка {CONTENT_DIR} не найдена!")
        return

    # Находим все .md файлы во всех подпапках (blogs, projects и т.д.)
    md_files = list(CONTENT_DIR.rglob("*.md"))
    print(f"Найдено файлов: {len(md_files)}")

    for file in md_files:
        translate_markdown_file(file)
            
    print("\n--- Готово! ---")

if __name__ == "__main__":
    main()