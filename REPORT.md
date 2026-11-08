# Отчет по настройке отображения заметок Obsidian на главной странице Flask-приложения

## Проект
Путь: `c:\Projects\MyFlask`
Тип приложения: Flask с использованием flask_flatpages и flask_frozen

## Конфигурация Obsidian Vault

### 1. config.ini
Файл: `c:\Projects\MyFlask\api\config.ini`
```ini
[configs]
domain = http://rad.sloboda43.netcraze.pro
email = alexnaos@gmail.com
your_name = Золотов Алексей
github = https://github.com/alexnaos

; ... other config options ...

; ================== OBSIDIAN ==================
; Путь к папке вашего хранилища Obsidian (ваулту).
obsidian_vault = C:\\YandexDisk\\Obsidian Vault

; Заметки из Obsidian с этим полем в начале будут показаны на сайте.
obsidian_publish_key = publish
```

### 2. index.py - Настройка пути к vault
Файл: `c:\Projects\MyFlask\api\index.py`, строка 26:
```python
OBSIDIAN_VAULT = r"C:\\YandexDisk\\Obsidian Vault"
```
Путь также читается из config.ini через `_file_config()` если указано в секции `[configs]`.

### 3. Функция чтения заметок
Функция `read_obsidian_notes(vault_path, limit)` в `index.py`:
- Чтение `.md` файлов из директории vault
- Парсинг YAML front matter
- Извлечение title, date, published status
- Сортировка по времени модификации (новые первыми)
- Ограничение количества заметок параметром `limit`


### Путь к vault проверен
- Папка `C:\YandexDisk\Obsidian Vault` существует
- Содержит 38 файлов `.md`
- Файлы содержат front matter с `publish: true`



Я хочу переписать главную страницу (маршрут `/` или `index`) в текущем проекте Flask, чтобы вместо стандартного контента на ней отображалась таблица моих заметок из реального Obsidian Vault.

Вот исходные данные и требования:
1. Путь к моему Obsidian Vault на компьютере: `C:\YandexDisk\Obsidian Vault`
2. На главной странице должна рендериться HTML-таблица со следующими колонками:
   - Название заметки (без расширения .md) — это должна быть ссылка на саму заметку.
   - Дата изменения файла.
   - Размер файла.
3. Логика работы бэкенда (Flask):
   - Написать функцию, которая сканирует указанную папку `C:\YandexDisk\Obsidian Vault`.
   - Читать только файлы с расширением `.md`. Игнорировать служебную папку `.obsidian` и файлы внутри неё.
   - Сортировать заметки по дате изменения (сначала свежие).
   - Передавать этот список в шаблон `index.html`.
4. Важное требование к ссылкам на заметки:
   - В Obsidian названия файлов часто содержат пробелы и кириллицу (например, "Техника для ПОС.md").
   - Настрой роутинг во Flask и генерацию ссылок в шаблоне так, чтобы сервер корректно обрабатывал URL-запросы с закодированной кириллицей (используй `urllib.parse.unquote` при получении имени файла на бэкенде), и при клике на название открывалась страница с содержимым этой заметки.
5. Обнови файлы:
   - Бэкенд-код (где инициализируется Flask и прописаны роуты).
   - Шаблон `index.html` (добавь аккуратную адаптивную HTML-таблицу).

Сделай изменения минималистичными, не ломая общую структуру проекта flask-portfolio. Выведи только исправленный код.



cd C:\Projects\MyFlask\api\static
pandoc "C:\YandexDisk\Я_док\РезюмеЗолотовГИП.docx" -t markdown_strict --wrap=none --extract-media="images" -o "resume_dev.md"

git init; git add .; git commit -m "Initial commit"; git branch -M main; git remote add origin https://github.com/alexnaos/MyFlask.git; git push -u origin main

