# MyFlask Portfolio

Персональный сайт-портфолио на [Flask](https://flask.palletsprojects.com/) с интеграцией заметок из [Obsidian](https://obsidian.md/), блогом/проектами на Markdown (`Flask-FlatPages`), страницей резюме и возможностью автоматического запуска как службы Windows. Поддерживает развёртывание через Docker (вместе с проектом [ProjectCards](https://github.com/alexnaos/ProjectCards)) на Debian/Orange Pi.

> ⚠️ Это личный проект с данными автора. Перед публикацией своего форка обязательно проверьте `api/config.ini` и `.env` — там не должно быть ваших реальных паролей, ключей и личных путей.

---

## 📖 О проекте

Сайт объединяет профессиональный опыт в строительном проектировании и цифровизации с увлечением инженерией, электроникой и программированием:

* **Основное:** персональное портфолио и резюме (инженер-проектировщик, специалист по цифровизации строительства, разработчик IoT-систем).
* **Блог и проекты:** статьи и описания проектов в формате Markdown.
* **Obsidian:** автоматически подхватывает опубликованные заметки из вашего хранилища (ваулта) Obsidian.
* **Сервисы:** страница «О себе», поиск по блогу, sitemap/robots.txt, тёмная тема (Bootstrap 5.3).

### Контакты

* Сайт проекта: https://helpinv.ru
* Telegram: @helpinv
* Email: alexnaos@gmail.com / alexnaos@yandex.ru
* GitHub: github.com/alexnaos

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
| **Автозапуск Windows** | Waitress + NSSM — работает как служба (запуск вместе с Windows) |
| **Docker** | Сборка под `linux/amd64` и `linux/arm64` (Orange Pi), watchtower для автообновлений |

---

## 🛠️ Стек технологий

* **Python 3.11+**
* [Flask](https://flask.palletsprojects.com/) 3.0.3
* [Flask-FlatPages](https://python-flask-flatpages.readthedocs.io/) — блог и проекты из `.md`
* [Frozen-Flask](https://python-frozen-flask.readthedocs.io/) — статическая экспорт
* [Waitress](https://docs.pylonsproject.org/projects/waitress/) — production WSGI-сервер
* [gunicorn](https://gunicorn.org/) — сервер в контейнере
* [Markdown](https://Python-Markdown.github.io/) — рендеринг Markdown
* [NSSM](https://nssm.cc/) — служба Windows
* [Pandoc](https://pandoc.org/) — конвертация резюме из DOCX (опционально)
* [Bootstrap 5.3](https://getbootstrap.com/) — фронтенд
* Docker / Docker Compose — продакшен-развёртывание

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
├── deploy/
│   ├── README-FAILOVER.md  # Отказоустойчивость двух узлов (56 ↔ 103)
│   ├── windows/            # Конфиги Nginx/NSSM для Windows
│   ├── linux/              # Конфиги Nginx для Debian
│   └── orangepi/           # Настройки под Orange Pi
├── tests/
│   └── test_app.py         # Публичные роуты, резюме, заголовки безопасности, поиск
├── .dockerignore
├── .env.example            # Шаблон переменных окружения для docker-compose
├── .gitignore
├── Dockerfile              # Мультиплатформенный образ (MyFlask + ProjectCards)
├── docker-compose.yml      # Запуск через Docker Compose
├── requirements.txt
├── check_md_fields.py      # Скрипт добавления front matter в заметки
├── convert_resume.py       # Конвертация резюме
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
domain = http://127.0.0.1:5000
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

```bash
python api/index.py
```

Сайт будет доступен по адресу **http://127.0.0.1:5000**.

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

### 5. Тесты

```bash
pip install pytest
pytest
```

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

### `.env` (только Docker)

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

Ключевые переменные:

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `IMAGE` | `ghcr.io/alexnaos/myflask:latest` | Образ контейнера |
| `BIND_ADDR` | `0.0.0.0` | Адрес прослушивания (`127.0.0.1` для локального запуска) |
| `APP_PORT` | `8080` | Порт хоста |
| `HOST_YADISK_PATH` | `/srv/myflask/data` | Путь к данным на хосте (монтируется в `/data`) |
| `MYFLASK_CONTENT_DIR` | `/data/Obsidian Vault` | Путь к vault Obsidian внутри контейнера |
| `CARDS_CONTENT_DIR` | `/data` | Путь к карточкам ProjectCards |
| `PEER_HOST` | `192.168.1.103` | Соседний узел для nginx failover |

> `.env` уже добавлен в `.gitignore` — не коммитьте его.

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

> Вспомогательный скрипт `check_md_fields.py` помогает добавлять нужные поля в заметки пакетно.

---

## 🖥️ Запуск в продакшене

### Вариант A — Docker (рекомендуется для Linux/Orange Pi)

```bash
cp .env.example .env
# отредактируйте .env под свой хост
docker compose up -d
```

Сайт будет доступен на порту `APP_PORT` (по умолчанию 8080). Образ обновляется автоматически через **watchtower** (раз в час).

Сборка образа локально:

```bash
docker compose build
```

### Вариант B — Windows (Waitress + NSSM)

Установите Waitress:

```powershell
pip install waitress
```

Скачайте [NSSM](https://nssm.cc/download) и положите `nssm.exe` в корень проекта.

Создайте службу (PowerShell от имени администратора):

```powershell
.\nssm.exe install MyFlaskApp "C:\Путь\К\Python\python.exe" "-m waitress --listen=127.0.0.1:8080 api:index"
.\nssm.exe set MyFlaskApp AppDirectory "C:\Projects\MyFlask"
.\nssm.exe set MyFlaskApp AppExit Default Restart
.\nssm.exe start MyFlaskApp
```

Сайт будет доступен по `http://127.0.0.1:8080`. Для внешнего доступа используйте Nginx в качестве reverse-proxy (конфиги см. в `deploy/windows/`).

> Скрипт `run_server.py`, упоминаемый в более ранних версиях, отсутствует — используйте встроенный модуль `waitress` (см. пример выше) или создайте собственный entrypoint.

---

## 🔁 Отказоустойчивость (двух узлов)

Проект рассчитан на работу на двух узлах (Windows 56 + Debian 103) с авто-переключением через Nginx:

* **56 (Windows):** Nginx :80 → основной `103:8080`, резерв `127.0.0.1:8080`.
* **103 (Debian):** Docker-контейнер :8080 → основной `127.0.0.1:8080`, резерв `56:8080`.
* Домен `rad.sloboda43.netcraze.pro` направляется роутером на один живой узел.

Подробности: `deploy/README-FAILOVER.md`.

---

## 🔒 Безопасность

* `api/config.ini` и `.env` содержат личные данные — не публикуйте их в открытом репозитории.
* `.gitignore` уже исключает `.env`, `*.log`, `REPORT.md`, `DIAGNOSTICS_*.md`, `DEPLOY_*.md`, `nssm.exe`.
* Применяются заголовки безопасности: `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`.

---

## 🤝 Вклад

1. Форкните репозиторий.
2. Создайте ветку `git checkout -b feature/ваша-тема`.
3. Внесите изменения и проверьте их тестами (`pytest`).
4. Отправьте Pull Request.

---

## 📄 Лицензия

Личный проект. Используйте код на свой страх и риск.

---

**Автор:** Золотов Алексей — инженер-проектировщик, специалист по цифровизации строительства, разработчик IoT-систем.  
GitHub: https://github.com/alexnaos | Email: alexnaos@gmail.com
