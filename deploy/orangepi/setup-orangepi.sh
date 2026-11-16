#!/usr/bin/env bash
# =============================================================================
# Подготовка основного сервера Orange Pi (Debian/ARM64):
#  1) rclone + автомонтирование Яндекс.Диска в /mnt/yadisk (systemd)
#  2) Docker + Docker Compose
#  3) Рабочая директория /opt/flask-mirror (compose + .env)
# Для ПЕРВОГО запуска rclone потребуется интерактивная авторизация.
# Запускать от пользователя alex (sudo запросит пароль).
# =============================================================================
set -euo pipefail

echo '==> [1/4] Обновление и базовые пакеты'
sudo apt-get update
sudo apt-get install -y curl unzip ripgrep fuse3 ca-certificates

echo '==> [2/4] Установка rclone'
if ! command -v rclone >/dev/null 2>&1; then
    curl -O https://downloads.rclone.org/rclone-current-linux-arm64.zip
    unzip -o rclone-current-linux-arm64.zip
    sudo cp rclone-*-linux-arm64/rclone /usr/bin/rclone
    sudo chmod 755 /usr/bin/rclone
    rm -rf rclone-*-linux-arm64 rclone-current-linux-arm64.zip
fi
rclone version

echo '==> [3/4] Установка Docker + Compose'
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USER"
sudo systemctl enable --now docker
docker --version
docker compose version

echo '==> [4/4] Структура для контента и проекта'
# rclone конфиг (интерактивная авторизация): сохраните сессию в yadisk:
#   rclone config -> n -> name=yadisk -> type=drive? НЕТ: для Яндекс.Диска remote=WebDAV, url=https://webdav.yandex.ru
sudo mkdir -p /mnt/yadisk /opt/flask-mirror
sudo chown "$USER":"$USER" /mnt/yadisk /opt/flask-mirror

# systemd-юнит монтирования
sudo cp "$(dirname "$0")/rclone-yadisk.service" /etc/systemd/system/rclone-yadisk.service
sudo systemctl daemon-reload
sudo systemctl enable rclone-yadisk.service

echo
echo '================================================================='
echo 'Дальше вручную:'
echo  1) rclone config   # создайте remote "yadisk" (WebDAV: https://webdav.yandex.ru)
echo  2) sudo systemctl start rclone-yadisk.service; mount | grep yadisk
echo  3) скопируйте docker-compose.yml в /opt/flask-mirror
echo  4) создайте /opt/flask-mirror/.env из deploy/orangepi/.env.production.example
echo  5) cd /opt/flask-mirror && docker compose pull && docker compose up -d
echo '================================================================='
echo 'Авторизация rclone': после `rclone config` откроется веб-ссылка Яндекс.Диска —
echo 'перейдите по ней в браузере, авторизуйтесь и вставьте полученный токен.'