# MyFlask Portfolio

Персональный сайт-портфолио на Flask с интеграцией заметок Obsidian, страницей резюме и автоматическим запуском на Windows.

## ✨ Возможности

- **Главная страница**: Отображение последних заметок из вашего хранилища Obsidian (с поддержкой сортировки таблицы по названию и дате).
- **Блог и Проекты**: Работа на основе библиотеки `Flask-FlatPages` (файлы `.md` в папке `content`).
- **Страница Резюме**: Отображение резюме в формате Markdown с поддержкой вкладок (настраивается через `config.ini`) и корректным выводом картинок.
- **Автоматический запуск**: Скрипт `run_server.py` использует `Waitress` и `NSSM` для работы в качестве службы Windows (запускается вместе с системой).
- **Тёмная тема**: Использование Bootstrap 5.3 с адаптивным дизайном.

## 🛠️ Стек технологий

- Python 3.14+
- Flask
- Flask-FlatPages
- Flask-Frozen
- Waitress (для production-сервера)
- NSSM (для создания службы Windows)
- Pandoc (для конвертации резюме из DOCX)
- Bootstrap 5.3

## 🚀 Быстрый старт (разработка)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ваш_ник/MyFlask.git
   cd MyFlask

   Установите зависимости:

bash
pip install -r requirements.txt
Настройте конфигурацию:
Отредактируйте api/config.ini, указав свои данные (имя, email, путь к хранилищу Obsidian и т.д.).

Запустите сервер разработки:

bash
python api/index.py

Запустите сервер разработки:

bash
python api/index.py
Сайт будет доступен по адресу http://127.0.0.1:5000.
🖥️ Установка как службы Windows (Production)
Для автоматического запуска при загрузке системы используется связка Waitress + NSSM.

Установите Waitress:

bash
pip install waitress
Скачайте NSSM с официального сайта и положите nssm.exe в корень проекта.

Создайте службу (в PowerShell от имени Администратора):
powershell
.\nssm.exe install MyFlaskApp "C:\Python314\python.exe" "C:\Projects\MyFlask\run_server.py"
.\nssm.exe set MyFlaskApp AppDirectory "C:\Projects\MyFlask"
.\nssm.exe set MyFlaskApp AppExit Default Restart
.\nssm.exe start MyFlaskApp
📁 Структура проекта
text
MyFlask/
├── api/
│   ├── config.ini          # Настройки сайта и путей
│   ├── index.py            # Основной код Flask-приложения
│   ├── content/            # Markdown-файлы для блога и проектов
│   ├── static/             # Картинки, CSS, файлы резюме (resume.md)
│   └── templates/          # HTML-шаблоны (Jinja2)
├── .gitignore
├── requirements.txt
├── run_server.py           # Скрипт запуска через Waitress для службы Windows
└── README.md
📝 Как добавить контент
Блог: Создайте файл .md в api/content/blogs/ с заголовком в формате YAML (см. примеры).

Проекты: Создайте файл .md в api/content/projects/.

Резюме: Отредактируйте api/static/resume.md. Для добавления вкладок используйте секцию [resumes] в api/config.ini.

⚠️ Важно
Файл config.ini содержит ваши личные данные. При публикации в открытый репозиторий убедитесь, что там нет паролей или API-ключей.

Для корректного отображения картинок из Pandoc в index.py предусмотрена автоматическая замена путей.



C:\Projects\MyFlask\check_md_fields.py
Скрипт добавления полей в заметки
---
date: 'сегодня'
publish: true
title: Название заметки
---