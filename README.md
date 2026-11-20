# MyFlask Portfolio

Персональный сайт-портфолио на [Flask](https://flask.palletsprojects.com/) с интеграцией заметок из [Obsidian](https://obsidian.md/), блогом/проектами на Markdown (`Flask-FlatPages`) и страницей резюме.

> ⚠️ Это личный проект с данными автора. Перед публикацией своего форка обязательно проверьте `api/config.ini` — там не должно быть ваших реальных паролей, ключей и личных путей.

---

## 📖 О проекте

Сайт объединяет профессиональный опыт в строительном проектировании и цифровизации с увлечением инженерией, электроникой и программированием:

* **Основное:** персональное портфолио и резюме.
* **Блог и проекты:** статьи и описания проектов в формате Markdown.
* **Obsidian:** автоматически подхватывает опубликованные заметки из вашего хранилища (ваулта) Obsidian.
* **Сервисы:** страница «О себе», поиск по блогу, sitemap/robots.txt, тёмная тема (Bootstrap 5.3).

---

## ✨ Возможности

| Возможность | Описание |
|-------------|----------|
| **Главная страница** | Последние заметки из хранилища Obsidian с сортировкой по названию и дате |
| **Блог** | Статьи в `api/content/blogs/` на базе `Flask-FlatPages` (YAML front matter) |
| **Проекты** | Карточки проектов в `api/content/projects/` |
| **Резюме** | Страница `/resume` с вкладками (настраивается через `api/config.ini`) |
| **Поиск** | Поисковый запрос по публикациям блога (`/blog/search`) |
| **SEO** | `robots.txt`, `sitemap.xml`, OpenGraph/description/canonical |
| **Тёмная тема** | Bootstrap 5.3, адаптивная вёрстка |

---

## 🛠️ Стек технологий

* **Python 3.11+**
* [Flask](https://flask.palletsprojects.com/) 3.0.3
* [Flask-FlatPages](https://python-flask-flatpages.readthedocs.io/) — блог и проекты из `.md`
* [Frozen-Flask](https://python-frozen-flask.readthedocs.io/) — статическая экспорт
* [Markdown](https://Python-Markdown.github.io/) — рендеринг Markdown
* [Bootstrap 5.3](https://getbootstrap.com/) — фронтенд

---

## 📁 Структура проекта

```
MyFlask/
├── api/
│   ├── config.ini          # Настройки сайта (имя, email, пути, соцсети, Obsidian, вкладки резюме)
│   ├── index.py            # Точка входа Flask-приложения (create_app)
│   ├── content/
│   │   ├── blogs/          # Статьи блога (*.md с YAML front matter)
│   │   └── projects/       # Карточки проектов (*.md)
│   ├── static/
│   │   ├── resume.md       # Основное резюме (Markdown)
│   │   ├── resume_dev.md   # Резюме для вкладки «Разработка»
│   │   ├── resume.pdf      # PDF-вариант резюме
│   │   ├── index.js        # Клиентский JS
│   │   └── images/         # Фото, иконки, вложения
│   └── templates/          # Jinja2-шаблоны (base.html, about.html, ...)
├── requirements.txt
└── README.md
```

---

## 🚀 Быстрый старт (разработка)

### 1. Клонирование

```bash
git clone https://github.com/alexnaos/MyFlask.git
cd MyFlask
```

### 2. Виртуальное окружение и зависимости

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Настройка конфигурации

Отредактируйте `api/config.ini`:

```ini
[configs]
domain = http://127.0.0.1:8080
email = ваша@почта.ru
your_name = Имя Фамилия
github = https://github.com/ваш_ник
telegram = https://t.me/ваш_ник
vk = https://vk.com/...
twitter = https://x.com/...

; Путь к хранилищу Obsidian (оставьте пустым, если не нужно)
obsidian_vault = C:/Путь/К/Obsidian Vault
obsidian_publish_key = publish

[resumes]
main = resume.md | Основное
dev = resume_dev.md | Разработка
```

### 4. Запуск сервера разработки

Есть два способа запуска:

**Способ 1: Через основной файл**
```bash
python api/index.py
```

**Способ 2: Через скрипт запуска**
```bash
python run.py
```

Сайт будет доступен по адресу **http://127.0.0.1:8080**.

Доступные маршруты:

* `/` — главная (заметки Obsidian)
* `/about` — страница «О себе»
* `/blog/` — список постов блога
* `/blog/<slug>` — отдельный пост
* `/blog/search` — поиск (POST, параметр `query`)
* `/projects/` — карточки проектов
* `/resume` — резюме (с вкладками)
* `/obsidian/<path>` — просмотр заметки из vault
* `/schematics/ats`, `/schematics/shield` — панели схемами
* `/robots.txt`, `/sitemap.xml`

---

## ⚙️ Конфигурация

### `api/config.ini`

Содержит секции:

* `[configs]` — общие настройки сайта (домен, email, имя, соцсети, путь к Obsidian, ключ публикации).
* `[resumes]` — вкладки резюме. Формат: `ключ = имя_файла.md | Название вкладки`.

Пример добавления вкладки:

```ini
[resumes]
main = resume.md | Основное
dev  = resume_dev.md | Разработка
pm   = resume_pm.md  | Менеджмент
```

---

## 📝 Как добавить контент

### Блог

Создайте файл `api/content/blogs/<имя>.md` с YAML front matter:

```markdown
---
title: Заголовок статьи
date: 2024-01-15
publish: true
---

Текст статьи в Markdown.
```

### Проекты

Создайте файл `api/content/projects/<имя>.md`:

```markdown
---
title: Название проекта
date: 2024-01-10
publish: true
---

Описание проекта.
```

### Резюме

Отредактируйте `api/static/resume.md`. Для вкладок добавьте записи в секцию `[resumes]` файла `api/config.ini` (см. раздел «Конфигурация»).

### Obsidian

1. Укажите путь к вашему vault в `api/config.ini` (`obsidian_vault`) или переменной `MYFLASK_CONTENT_DIR`.
2. В начале заметки добавьте front matter:

```markdown
---
publish: true
title: Заголовок заметки
date: 2024-01-15
---
```

Только заметки с ключом `obsidian_publish_key` (по умолчанию `publish: true`) отображаются на сайте.

---

## 📄 Лицензия

Личный проект. Используйте код на свой страх и риск.

---

**Автор:** Золотов Алексей — инженер-проектировщик, специалист по цифровизации строительства, разработчик IoT-систем.  
GitHub: https://github.com/alexnaos | Email: alexnaos@gmail.com
