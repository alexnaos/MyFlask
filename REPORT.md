# Отчет по настройке отображения заметок Obsidian на главной странице Flask-приложения



.\nssm.exe restart MyFlaskApp     


cd C:\Projects\MyFlask\api\static
pandoc "C:\YandexDisk\Я_док\РезюмеЗолотовГИП.docx" -t markdown_strict --wrap=none --extract-media="images" -o "resume_dev.md"


alex@debian:~/convertx$ openssl rand -hex 32
3c8e495e905ccb0483bf1790739e030ef5a58bba9d2039ffeadbad2496ed5fcf
alex@debian:~/convertx$ 



cd C:\Projects\MyFlask\api\static
pandoc "C:\YandexDisk\Я_док\РезюмеЗолотовГИП.docx" -t markdown_strict --wrap=none --extract-media="images" -o "resume_dev.md"

git init; git add .; git commit -m "Initial commit"; git branch -M main; git remote add origin https://github.com/alexnaos/MyFlask.git; git push -u origin main





# Промт для агента

Скопируйте целиком:

---

Реализуй поиск по заметкам Obsidian на главной странице `api/templates/home.html`. Поиск — **только на стороне клиента (JavaScript)**, без новых серверных endpoint-ов и без перезагрузки страницы. Заметок ~79, фильтрация в браузере мгновенная.

## Требования

### 1. HTML — поле поиска
Перед блоком `<table id="notesTable">` вставить:

```html
<div class="mb-3">
  <input type="search" id="obsidianSearch"
         class="form-control form-control-sm"
         placeholder="Поиск по заметкам Obsidian…"
         aria-label="Поиск заметок Obsidian"
         autocomplete="off">
</div>
<div id="noResults" class="text-muted small mt-2" hidden>Заметки не найдены</div>
```

Требования к полю:
- `type="search"` (встроенный крестик очистки), НЕ `type="text"`.
- `autocomplete="off"`.
- `#noResults` — **отдельный `<div>` под таблицей**, не `<tr>` внутри `<tbody>`.

### 2. Атрибут `data-search` на каждой строке
При рендере каждой `<tr>` в `<tbody>` таблицы `#notesTable` добавить атрибут:

```html
<tr data-search="название дата путь">
```

где значение — «сырые» данные строки (название заметки, дата, путь), приведённые к нижнему регистру и с заменой `ё → е`. Разделитель — пробел. **Не полагаться на `textContent`** при фильтрации — использовать `data-search`.

Если строки рендерятся в шаблоне Jinja2 — сформировать значение в шаблоне, например:

```html
<tr data-search="{{ (note.title ~ ' ' ~ note.date ~ ' ' ~ note.path)|lower|replace('ё','е') }}">
```

(подставь реальные имена переменных из текущего шаблона).

### 3. JavaScript — фильтрация

В существующем блоке `<script>` добавить:

```js
(function () {
  const input = document.getElementById('obsidianSearch');
  const table = document.getElementById('notesTable');
  const noResults = document.getElementById('noResults');
  if (!input || !table) return;

  const norm = s => s.toLowerCase().replace(/ё/g, 'е');

  function filterObsidianNotes() {
    const q = norm(input.value.trim());
    const rows = table.querySelectorAll('tbody tr');
    let visible = 0;
    rows.forEach(tr => {
      const hay = tr.dataset.search || norm(tr.textContent);
      const ok = q === '' || hay.includes(q);
      tr.style.display = ok ? '' : 'none';
      if (ok) visible++;
    });
    noResults.hidden = visible > 0;
  }

  input.addEventListener('input', filterObsidianNotes);

  // Escape — очистить поле и сбросить фильтр
  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      input.value = '';
      filterObsidianNotes();
    }
  });
})();
```

Требования:
- Событие `input` (не `keyup`), без `debounce` — при 79 строках не нужен.
- Пустой запрос → показать все строки, скрыть `#noResults`.
- Нормализация `ё → е` на обеих сторонах (запрос и данные) — через `norm()`.
- Селектор строк — строго `#notesTable tbody tr`, чтобы не зацепить `<thead>`.
- Не ломать существующий JS в файле.

### 4. CSS (минимально)
Добавить только отступ для поля поиска, если он не покрывается Bootstrap-классом `mb-3`. Подсветку совпадений (`<span class="highlight">`) **не делать** — вне scope.

## Что НЕ делать
- Не создавать серверный endpoint `/obsidian/search`.
- Не искать по телу markdown-заметок.
- Не добавлять пагинацию.
- Не использовать `debounce`.
- Не вставлять «Заметки не найдены» как `<tr>`.
- Не менять другие страницы и не рефакторить существующий код за пределами описанного.

## После реализации
1. Покажи дифф по `api/templates/home.html` (или изменённые фрагменты).
2. Перезапусти сервер.
3. Выполни в PowerShell:

```powershell
(Invoke-WebRequest -Uri 'http://192.168.1.56:8080/' -UseBasicParsing).Content -split "`n" | Select-String -Pattern 'obsidianSearch','data-search','noResults'
```

и покажи, что элементы присутствуют в отрендеренном HTML.
4. Напиши, что именно я должен проверить вручную в браузере (ввод «тест», «ё», пустой запрос, Escape).

---

Если что-то в текущем `home.html` не совпадает с описанным (другие имена переменных, структура таблицы) — сначала покажи мне проблемный фрагмент и спроси, как поступить, **не угадывай**.




ЗАДАЧА: Интегрировать две готовые HTML-схемы в существующий Flask-проект MyFlask
как отдельный раздел «Схемы щита».

КОНТЕКСТ ПРОЕКТА:
- Стек: Python 3.14, Flask, Flask-FlatPages, Jinja2, Bootstrap 5.3, Waitress.
- Главный файл приложения: api/index.py
- Шаблоны: api/templates/ (там уже есть base.html с navbar)
- Статика: api/static/
- Запуск: python api/index.py → http://127.0.0.1:5000
- Тёмная тема уже настроена через Bootstrap 5.3.

ИСХОДНЫЕ ФАЙЛЫ (я приложу их отдельно в чат или они лежат в корне проекта):
1. ats_panel.html — схема АВР TOMZN + промежуточное реле + GX16 (880×640 SVG).
2. shield.html — схема щитка, две вкладки через JS: «все соединения» и «щиток + АВР».

============================
ШАГ 1. Разместить шаблоны
============================
Скопировать оба файла в api/templates/ сохранив имена:
- api/templates/ats_panel.html
- api/templates/shield.html

ВАЖНО: внутри файлов нет Jinja-конфликтов ({{ или {%), но на всякий случай
выполнить поиск по ним: если найдётся — обернуть проблемные участки
в {% raw %}...{% endraw %}.

============================
ШАГ 2. Добавить маршруты в api/index.py
============================
Найти место, где регистрируются @app.route (рядом с index, blog, projects,
resume — по фактической структуре файла). Добавить:

    @app.route('/schematics')
    def schematics():
        return redirect(url_for('schematics_ats'))

    @app.route('/schematics/ats')
    def schematics_ats():
        return render_template('ats_panel.html', current='ats')

    @app.route('/schematics/shield')
    def schematics_shield():
        return render_template('shield.html', current='shield')

Если redirect/url_for ещё не импортированы — добавить в существующую строку
from flask import ...

============================
ШАГ 3. Добавить навигацию в оба шаблона
============================
В файлах ats_panel.html и shield.html сразу после открывающего <body>
вставить ОДИН И ТОТ ЖЕ блок навигации (см. ниже). Это единственная правка
внутри самих схем — остальной SVG/JS не трогать.

    <nav style="display:flex;gap:22px;align-items:center;padding:12px 20px;
                background:#141722;border:1px solid #242936;border-radius:8px;
                margin:0 auto 20px;max-width:1300px;font:13px/1.4 system-ui;">
      <a href="{{ url_for('index') }}"
         style="color:#959da5;text-decoration:none;">← На главную</a>
      <a href="{{ url_for('schematics_ats') }}"
         style="text-decoration:none;
                color:{{ '#fff' if current == 'ats' else '#959da5' }};
                font-weight:{{ '600' if current == 'ats' else '400' }};">
         Схема АВР + реле + GX16
      </a>
      <a href="{{ url_for('schematics_shield') }}"
         style="text-decoration:none;
                color:{{ '#fff' if current == 'shield' else '#959da5' }};
                font-weight:{{ '600' if current == 'shield' else '400' }};">
         Щиток: все соединения
      </a>
    </nav>

Если url_for('index') не совпадает с реальным именем главной функции —
найти правильное имя в api/index.py и использовать его.

============================
ШАГ 4. Пункт в основном меню (base.html)
============================
В api/templates/base.html найти <ul class="navbar-nav ..."> (главное меню)
и добавить пункт в том же стиле, что и соседние:

    <li class="nav-item">
      <a class="nav-link" href="{{ url_for('schematics_ats') }}">Схемы щита</a>
    </li>

Если у ссылок есть active-состояние через request.endpoint — добавить
условие class="nav-link {{ 'active' if request.endpoint == 'schematics_ats'
or request.endpoint == 'schematics_shield' or request.endpoint == 'schematics' }}".

============================
ШАГ 5. Исправления в shield.html (логические + мобильные)
============================
5.1. Противоречие нумерации контакта реле.
    В ats_panel.html контакт подписан 11‑12 (NC), и это верно для логики
    «нет города → замыкание → старт». В shield.html тот же контакт
    нарисован как 11‑14 (это NO) и подписан «NC (11-14)» — исправить на 11‑12:

    Найти в shield.html:
        <text x="690" y="133" class="wl" fill="#fff" text-anchor="middle">14</text>
    Заменить на:
        <text x="690" y="133" class="wl" fill="#fff" text-anchor="middle">12</text>

    Также заменить текстовую подпись ««Сухой контакт» NC (11-14)» на
    ««Сухой контакт» NC (11-12)» и в блоке <p class="sub"> в конце.

5.2. Не менять больше НИЧЕГО в SVG/JS схем.

============================
ШАГ 6. Адаптивность и доступность (в оба файла)
============================
6.1. В ats_panel.html заменить:
        <svg width="880" height="640" viewBox="0 0 880 640" ...>
    на:
        <svg viewBox="0 0 880 640" ... style="width:100%;height:auto;max-width:880px;">

6.2. В <style> обоих файлов добавить в конец:

    @media (prefers-reduced-motion: reduce) {
      .running, .live-wire { animation: none !important; }
    }

============================
ШАГ 7. Проверка
============================
7.1. Запустить python api/index.py
7.2. Открыть:
    - http://127.0.0.1:5000/schematics        → редирект на /schematics/ats
    - http://127.0.0.1:5000/schematics/ats    → схема АВР, кнопки переключения
                                                режимов «Город / Генератор» работают,
                                                подсветка проводов меняется
    - http://127.0.0.1:5000/schematics/shield → две вкладки, переключение работает
    - http://127.0.0.1:5000/                  → в navbar есть «Схемы щита», клик ведёт
                                                на /schematics/ats
7.3. Сузить окно браузера до ~400px — SVG должен масштабироваться, не обрезаться.
7.4. Проверить, что /schematics/ats и /schematics/shield не сломали работу
    существующих страниц (главная, блог, проекты, резюме).

============================
ОГРАНИЧЕНИЯ
============================
- НЕ переписывать SVG на Jinja-макросы.
- НЕ менять существующие маршруты, шаблоны и логику, кроме перечисленного.
- НЕ добавлять новые зависимости в requirements.txt.
- НЕ трогать api/config.ini.
- Стиль существующего кода сохранять (отступы, имена, комментарии).
- Если какой-то шаг не соответствует фактической структуре проекта — 
  остановиться и сообщить, какой именно и почему, перед тем как 
  вносить изменения.

============================
РЕЗУЛЬТАТ
============================
Список изменённых/добавленных файлов с кратким описанием правок и 
подтверждение по чек-листу Шага 7.

