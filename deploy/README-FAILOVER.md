# Отказоустойчивость MyFlask (56 ↔ 103)

Схема: **оба сервера держат сайт**, входящий трафик отдаёт здоровый узел.

```
                  rad.sloboda43.netcraze.pro
                            │
                 роутер Netcraze (порт 80)
                   ┌────────┴────────┐
                   ▼                 ▼
            56 (Windows)       103 (Debian)
            nginx :80           nginx :80
            └─ upstream         └─ upstream
               local :8080         local :8080  (Docker, основной)
               backup: 103:8080    backup: 56:8080 (backup)
```

## Узлы и их сервисы

| Узел | IP | Сайт | Вход | Данные |
|---|---|---|---|---|
| **Debian 103** | 192.168.1.103 | Docker `myflask-app` :8080 | nginx :80 (опц.) | `/srv/myflask/data` (sync с 56, фоллбек WebDAV) |
| **Windows 56** | 192.168.1.56 | нативный `combined_app.py` :8080 (NSSM) или Docker | nginx :80 | `C:\YandexDisk` (локально) |

## Как работает failover

1. **56 (Windows)**: Nginx :80 → `upstream flask_app`: основной `192.168.1.103:8080`,
   резерв `127.0.0.1:8080` (локальный сервис/контейнер).
   → если 103 недоступен, Nginx сам переключает на локальный сервис на 56.

2. **103 (Debian)**: Nginx :80 → `upstream flask_app`: основной `127.0.0.1:8080`
   (локальный Docker), резерв `192.168.1.56:8080`.
   → если 56 недоступен, 103 сам обслуживает трафик.

3. **Домен `rad.sloboda43.netcraze.pro`** в роутере направляется на **один живой узел:
   либо 56, либо 103**. 
   - Внешний трафик с порта 80 роутера → на 56 (по умолчанию);
   - если 56 лежит — перенаправить порт 80 на 103 в панели роутера (Netcraze).

## Настройка

### На 56 (Windows)
Уже стоит нативный сервис `combined_app.py` (NSSM, порт 8080) и Nginx :80.

1. Обновить конфиг Nginx (основной 103 вместо 23):
   ```powershell
   Copy-Item deploy/windows/nginx.conf C:\nginx\conf\nginx.conf -Force
   C:\nginx\nginx.exe -t -p C:\nginx\
   nssm.exe restart MyFlaskNginx   # или: C:\nginx\nginx.exe -s reload
   ```
2. (Альтернатива Docker вместо нативного сервиса — опционально)
   ```powershell
   docker compose -f deploy/windows/docker-compose.windows.yml up -d
   ```
   Только не оставляйте одновременно нативный NSSM-сервис и контейнер на :8080 —
   сначала остановите нативный: `nssm.exe stop MyFlaskApp`.

### На 103 (Debian)
1. Контейнер уже слушает :8080:
   ```bash
   cd /opt/flask-mirror && docker compose up -d
   ```
2. Вход :80 (если роутер сможет слать домен на 103):
   ```bash
   sudo apt-get install -y nginx
   sudo cp deploy/linux/nginx-failover-103.conf /etc/nginx/conf.d/myflask-failover.conf
   # удалить дефолтный server на :80, если он конфликтует
   sudo nginx -t && sudo systemctl restart nginx
   ```

## Переключение домена при аварии

**Если лёг 56** → в панели роутера Netcraze укажите для домена/порта 80 адрес **192.168.1.103**.
**Если лёг 103** → трафик идёт через 56 автоматически (nginx failover на `127.0.0.1:8080`),
ничего переключать не нужно (пока 56 жив).

## Синхронизация данных (103)
103 получает контент с 56 по SSH (`C:\YandexDisk` → `/srv/myflask/data`) каждые 2 минуты;
если 56 недоступен — фоллбек на WebDAV. Скрипт: `/srv/myflask/sync-yadisk.sh`.
```
systemctl status myflask-sync.timer
```

## Проверка
```bash
curl -sI http://127.0.0.1:8080/                      # сам сервис
curl -sI http://192.168.1.56/                        # вход на 56 (:80)
curl -sI http://rad.sloboda43.netcraze.pro/          # внешний адрес
```
