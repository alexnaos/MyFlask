from __future__ import annotations
# ruff: noqa
import configparser
import os
import markdown
import re
import traceback
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from flask import Flask, Response, redirect, render_template, request, url_for
from flask_flatpages import FlatPages
from flask_frozen import Freezer


BASE_DIR = Path(__file__).resolve().parent
BLOG_DIRECTORY = "blogs"
PROJECT_DIRECTORY = "projects"
CONFIG_KEYS = (
    "domain",
    "email",
    "your_name",
    "github",
    "blog_comments",
    "hubspot",
    "linkedin",
    "twitter",
)


# Obsidian Vault path - читаем из config.ini или системной переменной
OBSIDIAN_VAULT = r"C:\YandexDisk\Obsidian Vault"

try:
    config_parser = configparser.ConfigParser()
    config_file = Path(__file__).resolve().parent.parent / "config.ini"
    if config_parser.read(str(config_file), encoding="utf-8"):
        if (
            config_parser.has_section("configs")
            and config_parser.get("configs", "obsidian_vault", fallback="").strip()
        ):
            OBSIDIAN_VAULT = config_parser.get("configs", "obsidian_vault").strip()
            OBSIDIAN_VAULT = OBSIDIAN_VAULT.strip('"').strip("'")
        if config_parser.has_section("configs"):
            _publish_key = config_parser.get("configs", "obsidian_publish_key", fallback="").strip()
            if _publish_key:
                OBSIDIAN_PUBLISH_KEY = _publish_key
except Exception:
    traceback.print_exc()


# Имя ключа front matter, по которому определяются заметки для публикации в Obsidian.
# Читается из config.ini (секция [configs], ключ obsidian_publish_key), по умолчанию "publish".
# Пример front matter в заметке: publish: true
OBSIDIAN_PUBLISH_KEY = "publish"


def _scan_obsidian_vault(vault_path: str) -> list[dict]:
    """Scan the Obsidian vault directory and return a list of note info dicts.
    Each dict contains: title, date, path
    Only scans .md files at the top level (excluding .obsidian, system dirs).
    """
    notes = []
    vault = Path(vault_path)

    if not vault.exists():
        return notes

    # System directories to exclude
    excluded_dirs = {".obsidian", "esp32", "Google Keep", "Пенс"}

    try:
        for item in vault.iterdir():
            # Only process files, skip directories and system dirs
            if item.is_dir():
                # Skip excluded system directories
                if item.name in excluded_dirs:
                    continue
                # Recursively scan subdirectories but limit depth
                for sub_item in item.rglob("*.md"):
                    try:
                        metadata, body = _read_markdown_file(sub_item)
                        # Build relative path from vault
                        rel_path = sub_item.relative_to(vault)
                        notes.append(
                            {
                                "title": metadata.get(
                                    "title", os.path.splitext(sub_item.name)[0]
                                ),
                                "date": metadata.get("date", ""),
                                "path": str(rel_path),
                                "filepath": str(sub_item),
                            }
                        )
                    except Exception as e:
                        # Fallback: use filename as title and mtime as date
                        try:
                            mtime = os.path.getmtime(sub_item)
                            date_str = datetime.fromtimestamp(
                                mtime, tz=timezone.utc
                            ).strftime("%d.%m.%Y %H:%M")
                            title = os.path.splitext(sub_item.name)[0]
                            rel_path = sub_item.relative_to(vault)
                            notes.append(
                                {
                                    "title": title,
                                    "date": date_str,
                                    "path": str(rel_path),
                                    "filepath": str(sub_item),
                                }
                            )
                        except Exception:
                            pass
            elif (
                item.is_file()
                and item.suffix == ".md"
                and item.name not in excluded_dirs
            ):
                # Top-level .md files
                try:
                    metadata, body = _read_markdown_file(item)
                    rel_path = item.relative_to(vault)
                    notes.append(
                        {
                            "title": metadata.get(
                                "title", os.path.splitext(item.name)[0]
                            ),
                            "date": metadata.get("date", ""),
                            "path": str(rel_path),
                            "filepath": str(item),
                        }
                    )
                except Exception as e:
                    # Fallback: use filename as title and mtime as date
                    try:
                        mtime = os.path.getmtime(item)
                        date_str = datetime.fromtimestamp(
                            mtime, tz=timezone.utc
                        ).strftime("%d.%m.%Y %H:%M")
                        title = os.path.splitext(item.name)[0]
                        rel_path = item.relative_to(vault)
                        notes.append(
                            {
                                "title": title,
                                "date": date_str,
                                "path": str(rel_path),
                                "filepath": str(item),
                            }
                        )
                    except Exception:
                        pass
    except Exception as e:
        traceback.print_exc()

    # Sort by date descending (newest first), treating empty dates as oldest
    def sort_key(note):
        d = note.get("date", "")
        try:
            return datetime.strptime(d, "%Y-%m-%d") if d else datetime.min
        except ValueError:
            return datetime.min

    notes.sort(key=sort_key, reverse=True)
    return notes


def _is_truthy(value: str | None) -> bool:
    return bool(value and value.lower() in {"1", "true", "yes", "on"})


DEBUG = _is_truthy(os.getenv("FLASK_DEBUG"))
CONFIG_FILE = Path(os.getenv("SITE_CONFIG_PATH", BASE_DIR / "config.ini"))


@lru_cache(maxsize=1)
def _file_config() -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")
    return dict(parser.items("configs")) if parser.has_section("configs") else {}


def _parse_front_matter(content: str) -> tuple[dict, str]:
    """Parse YAML front matter from markdown content.
    Returns (metadata_dict, body_text).
    If no front matter found, returns empty dict and full content.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if match:
        front_matter_text = match.group(1)
        body = match.group(2)
        metadata = {}
        for line in front_matter_text.strip().split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                metadata[key.strip()] = value.strip()
        return metadata, body
    return {}, content


def _read_markdown_file(filepath: Path) -> tuple[dict, str]:
    """Read a markdown file and parse its front matter.
    Returns (metadata_dict, body_text).
    Falls back to file modification time if no date in front matter.
    Logs errors with traceback.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        metadata, body = _parse_front_matter(content)

        # Extract date from front matter
        date_str = metadata.get("date", "")

        # If no date in front matter, use file modification time
        if not date_str:
            try:
                file_time = os.path.getmtime(filepath)
                date_str = datetime.fromtimestamp(file_time, tz=timezone.utc).strftime(
                    "%Y-%m-%d"
                )
            except Exception:
                traceback.print_exc()
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        metadata["date"] = date_str
        metadata["published"] = metadata.get("published", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        return metadata, body

    except Exception:
        traceback.print_exc()
        # Return default metadata on error
        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "published": False,
            "title": filepath.stem if filepath.stem else "Unknown",
        }, ""


def site_config() -> dict[str, str]:
    if DEBUG:
        _file_config.cache_clear()
    defaults = _file_config()
    return {
        key: os.getenv(f"SITE_{key.upper()}", defaults.get(key, "")).strip()
        for key in CONFIG_KEYS
    }



def published_posts(flatpages: FlatPages, vault_path: str | None = None) -> list[dict]:
    """Get published notes from Flask-FlatPages."""
    # Всегда берем посты из папки content/blogs
    return [
        page
        for page in flatpages
        if page.path.startswith(f"{BLOG_DIRECTORY}/")
        and page.meta.get("published") is True
    ]

def read_obsidian_notes(vault_path: str | None = None, limit: int = 10) -> list[dict]:
    """Read markdown notes from Obsidian vault.
    Reads .md files from the vault directory recursively (including nested folders),
    parses front matter, and returns a list of note dictionaries.

    Only notes with front matter key equal to ``true`` (by default ``publish``,
    configurable via ``obsidian_publish_key`` in config.ini) are returned, e.g.:

        ---
        publish: true
        title: Моя заметка
        date: 2024-01-15
        ---

    Args:
        vault_path: Path to Obsidian vault. If None, uses configured path.
        limit: Maximum number of notes to return. Use 0 to return all notes.

    Returns:
        List of dictionaries with keys: title, date, published, path, body
    """
    notes = []

    if vault_path is None:
        vault_path = OBSIDIAN_VAULT

    vault_dir = Path(vault_path)

    if not vault_dir.exists():
        traceback.print_exc()
        return notes

    try:
        # Get all .md files recursively, including nested folders
        md_files = list(vault_dir.rglob("*.md"))

        # Filter out files in .obsidian directory and other non-note directories
        excluded_dirs = {".obsidian", ".git", "node_modules"}
        filtered_files = []

        for file_path in md_files:
            # Check if any parent directory is in excluded list
            parent_parts = file_path.parts
            if not any(part in excluded_dirs for part in parent_parts):
                filtered_files.append(file_path)

        # Sort by modification time, newest first
        filtered_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)

        # Read and parse each file, limit to requested number
        # limit=0 means return all notes
        read_files = filtered_files if limit == 0 else filtered_files[:limit]

        for file_path in read_files:
            try:
                metadata, body = _read_markdown_file(file_path)

                # Отображаем только заметки с ключом публикации = true (из config.ini: obsidian_publish_key)
                if not _is_truthy(metadata.get(OBSIDIAN_PUBLISH_KEY)):
                    continue

                # 1. Пытаемся взять title из метаданных
                title = metadata.get("title", "").strip()

                # 2. Если нет, берем имя файла без расширения
                if not title:
                    title = file_path.stem

                # 3. Если имя файла неинформативное, берем первую строку текста (если она не слишком длинная)
                if not title and body:
                    first_line = body.split("\n")[0].strip()
                    if first_line and len(first_line) < 80:
                        title = first_line

                # Use relative path from vault root for the path field
                rel_path = file_path.relative_to(vault_dir)
                note = {
                    "title": title,
                    "date": metadata.get("date", ""),
                    "published": metadata.get("published", False),
                    "path": str(rel_path),
                    "body": body,
                }
                notes.append(note)
            except Exception:
                traceback.print_exc()
                continue

    except Exception:
        traceback.print_exc()

    return notes


def newest(pages):
    return sorted(pages, reverse=True, key=lambda page: page.meta.get("date", ""))


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=BASE_DIR / "static",
        template_folder=BASE_DIR / "templates",
    )
    app.config.update(
        DEBUG=DEBUG,
        FLATPAGES_AUTO_RELOAD=DEBUG,
        FLATPAGES_EXTENSION=".md",
        FLATPAGES_ROOT=str(BASE_DIR / "content"),
    )

    flatpages = FlatPages(app)
    freezer = Freezer(app)
    app.extensions["flatpages_instance"] = flatpages
    app.extensions["freezer_instance"] = freezer

    @app.context_processor
    def template_context():
        config = site_config()
        domain = (
            config["domain"]
            .removeprefix("https://")
            .removeprefix("http://")
            .rstrip("/")
        )
        canonical_url = f"https://{domain}{request.path}" if domain else request.url
        return {
            **config,
            "canonical_url": canonical_url,
            "current_year": datetime.now(timezone.utc).year,
        }

    @app.after_request
    def security_headers(response: Response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        if request.is_secure or request.headers.get("X-Forwarded-Proto") == "https":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response

    @app.get("/")
    def home():
        """Home page with Obsidian notes table."""
        notes = read_obsidian_notes(limit=0)  # Show all notes, no limit
        return render_template("home.html", notes=notes)

    @app.get("/about")
    def about():
        return render_template("about.html")


    @app.get("/resume")
    def resume():
        # 1. Читаем конфиг
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE, encoding="utf-8")
        
        resumes_info = {}
        # Если секция [resumes] есть в конфиге, парсим её
        if parser.has_section("resumes"):
            for key, value in parser.items("resumes"):
                # Разделяем строку по символу "|" и убираем лишние пробелы
                parts = [p.strip() for p in value.split("|")]
                if len(parts) == 2:
                    resumes_info[key] = {"file": parts[0], "title": parts[1]}
        
        # Если секции нет или она пустая, ставим дефолт
        if not resumes_info:
            resumes_info = {"main": {"file": "resume.md", "title": "Основное"}}

        # 2. Определяем активную вкладку (из URL параметра ?tab=...)
        active_tab = request.args.get('tab', list(resumes_info.keys())[0])
        if active_tab not in resumes_info:
            active_tab = list(resumes_info.keys())[0]

        # 3. Читаем все файлы, указанные в конфиге
        all_resumes = {}
        for key, info in resumes_info.items():
            file_path = BASE_DIR / "static" / info["file"]
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    metadata, body = _parse_front_matter(content)
                    
                    # Чистим пути для картинок
                    body = body.replace('](images/', '](/static/images/')
                    body = body.replace('src="images/', 'src="/static/images/')
                    body = body.replace(str(BASE_DIR / "static") + "\\images\\", "/static/images/")
                    body = body.replace(str(BASE_DIR / "static") + "/images/", "/static/images/")
                    
                    # Убираем параметры ширины/высоты
                    body = re.sub(r'\{width="[^"]*"\s*height="[^"]*"\}', '', body)
                    body = re.sub(r'\{width="[^"]*"\}', '', body)
                    body = re.sub(r'\{height="[^"]*"\}', '', body)
                    
                    # Конвертируем в HTML
                    html_body = markdown.markdown(body, extensions=['fenced_code', 'tables'])
                    all_resumes[key] = html_body
                except Exception as e:
                    traceback.print_exc()
                    all_resumes[key] = f"Ошибка чтения файла {info['file']}: {e}"
            else:
                all_resumes[key] = f"Файл {info['file']} не найден в папке static."
                
        return render_template(
            "resume.html", 
            resumes=all_resumes, 
            resumes_info=resumes_info, 
            active_tab=active_tab
        )


    @app.get("/blog/")
    def posts():
        return render_template("blog.html", posts=newest(published_posts(flatpages)))

    @app.get("/post/<name>/")
    def post(name: str):
        page = flatpages.get_or_404(f"{BLOG_DIRECTORY}/{name}")
        if page.meta.get("published") is not True:
            return app.response_class(status=404)
        return render_template("blog-post.html", post=page)


    @app.post("/blog/search")
    def search_blog():
        query = request.form.get("query", "").strip()
        pages = published_posts(flatpages)
        if query:
            lowered = query.casefold()
            pages = [
                page
                for page in pages
                if lowered in page.body.casefold()
                or lowered in str(page.meta.get("title", "")).casefold()
            ]
        return render_template("blog.html", posts=newest(pages)[:10], query=query)

    @app.get("/obsidian/<path:path>")
    def obsidian_note(path):
        """Display an Obsidian note from the vault."""
        from pathlib import Path
        import re
        from urllib.parse import unquote

        vault_path = OBSIDIAN_VAULT
        # Декодируем URL-путь (на случай пробелов и кириллицы)
        decoded_path = unquote(path)
        file_path = os.path.join(vault_path, decoded_path)

        # Проверка безопасности: путь не должен выходить за пределы vault
        abs_vault = os.path.abspath(vault_path)
        abs_file = os.path.abspath(file_path)
        if not abs_file.startswith(abs_vault):
            return "Access denied", 403

        if not os.path.exists(file_path):
            return "Note not found", 404

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Парсим front matter (заголовок и дату)
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                front_matter = match.group(1)
                body = content[match.end() :]
                metadata = {}
                for line in front_matter.strip().split("\n"):
                    if ":" in line:
                        key, _, value = line.partition(":")
                        metadata[key.strip()] = value.strip()
            else:
                body = content
                metadata = {}

            title = metadata.get("title", os.path.splitext(os.path.basename(path))[0])

            return render_template(
                "obsidian-note.html",
                title=title,
                date=metadata.get("date", ""),
                body=body,
                path=path,
            )
        except Exception as e:
            traceback.print_exc()
            return f"Error reading note: {str(e)}", 500
       
    @app.route('/schematics')
    def schematics():
        return redirect(url_for('schematics_ats'))

    @app.route('/schematics/ats')
    def schematics_ats():
        return render_template('ats_panel.html', current='ats')

    @app.route('/schematics/shield')
    def schematics_shield():
        return render_template('shield.html', current='shield')

    @app.get("/robots.txt")
    def robots():
        return Response(
            f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n",
            mimetype="text/plain",
        )

      
    @app.get("/sitemap.xml")
    def sitemap():
        urls = [
            url_for("home", _external=True),
            url_for("about", _external=True),
            url_for("projects", _external=True),
            url_for("posts", _external=True),
        ]
        urls.extend(
            url_for(
                "post",
                name=page.path.removeprefix(f"{BLOG_DIRECTORY}/"),
                _external=True,
            )
            for page in published_posts(flatpages)
        )
        body = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{body}</urlset>",
            mimetype="application/xml",
        )

    return app


app = create_app()
flatpages: FlatPages = app.extensions["flatpages_instance"]
freezer: Freezer = app.extensions["freezer_instance"]


def search_posts(query: str):
    lowered = query.casefold()
    return [
        page for page in published_posts(flatpages) if lowered in page.body.casefold()
    ]


def get_latest_posts(limit: int = 10):
    return newest(published_posts(flatpages))[:limit]


if __name__ == "__main__":
    # Запускаем сервер на порту 5000
    app.run(host="127.0.0.1", port=5000, debug=True)
