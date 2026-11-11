#!/usr/bin/env python3
import os
from datetime import datetime
from pathlib import Path

# Путь к вашему хранилищу
VAULT_PATH = r"C:\YandexDisk"

def get_file_date(filepath):
    """Получает дату создания файла в формате YYYY-MM-DD"""
    try:
        ctime = os.path.getctime(filepath)
        return datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Очистка от предыдущего скрипта (удаляем строки, начинающиеся с "; ")
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            if line.startswith('; '):
                continue  # пропускаем сломанные строки
            clean_lines.append(line)
        
        content = '\n'.join(clean_lines).lstrip('\n')

        # 2. Поиск существующего YAML блока (между ---)
        front_matter_text = ""
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter_text = parts[1]
                body = parts[2].lstrip('\n')

        # 3. Анализ и исправление существующих ключей
        fm_lines = front_matter_text.split('\n')
        existing_keys = set()
        new_fm_lines = []
        
        file_name = Path(filepath).stem
        file_date = get_file_date(filepath)
        
        changed = False

        for line in fm_lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            if ':' in stripped:
                key, val = stripped.split(':', 1)
                key = key.strip()
                val = val.strip().strip("'\"") # убираем кавычки
                
                existing_keys.add(key)
                
                # Принудительно ставим publish: true
                if key == 'publish':
                    new_fm_lines.append('publish: true')
                    if val != 'true':
                        changed = True
                    continue
                
                # Исправляем дату, если там "сегодня" или пусто
                if key == 'date':
                    if val in ['сегодня', '', 'None']:
                        new_fm_lines.append(f'date: {file_date}')
                        changed = True
                    else:
                        new_fm_lines.append(f'date: {val}')
                    continue
                
                # Исправляем заголовок, если там дефолтный текст
                if key == 'title':
                    if val in ['Название заметки', 'Заголовок заметки', '']:
                        new_fm_lines.append(f'title: {file_name}')
                        changed = True
                    else:
                        new_fm_lines.append(f'title: {val}')
                    continue
                
                # Остальные поля оставляем как есть
                new_fm_lines.append(line)
            else:
                new_fm_lines.append(line)

        # 4. Добавление недостающих полей
        if 'publish' not in existing_keys:
            new_fm_lines.append('publish: true')
            changed = True
            
        if 'title' not in existing_keys:
            new_fm_lines.append(f'title: {file_name}')
            changed = True
            
        if 'date' not in existing_keys:
            new_fm_lines.append(f'date: {file_date}')
            changed = True

        # 5. Перезапись файла, если были изменения
        if changed or not front_matter_text:
            new_front_matter = '\n'.join(new_fm_lines)
            final_content = f"---\n{new_front_matter}\n---\n\n{body}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"Исправлен: {filepath}")

    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}")

def main():
    root = Path(VAULT_PATH)
    if not root.exists():
        print(f"Папка не найдена: {VAULT_PATH}")
        return

    count = 0
    for root_dir, dirs, files in os.walk(VAULT_PATH):
        # Пропускаем скрытые папки (например, .obsidian)
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root_dir, f)
                process_file(path)
                count += 1

    print(f"\nПроверено файлов: {count}")

if __name__ == "__main__":
    main()