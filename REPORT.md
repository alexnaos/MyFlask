# Отчет по настройке отображения заметок Obsidian на главной странице Flask-приложения


Нужно добавить в функцию чтения заметок из obsidian_vault = C:\YandexDisk\Obsidian Vault отображение всех в т.ч. во вложенных папках



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

