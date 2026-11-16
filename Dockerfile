# syntax=docker/dockerfile:1
# Мультиплатформенная сборка (linux/amd64 для Windows, linux/arm64 для Orange Pi).
# Контекст сборки должен содержать оба подпроекта: MyFlask/ и ProjectCards/.
# (см. .github/workflows/deploy.yml — он чекаутит оба репозитория).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MYFLASK_CONTENT_DIR="/data/Obsidian Vault" \
    CARDS_CONTENT_DIR="/data"


WORKDIR /app

# Сначала только requirements — слой с зависимостями кэшируется отдельно
COPY MyFlask/requirements.txt MyFlask/requirements.txt
COPY ProjectCards/requirements.txt ProjectCards/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        -r MyFlask/requirements.txt \
        -r ProjectCards/requirements.txt

# Копируем исходники обоих подпроектов
COPY MyFlask/ MyFlask/
COPY ProjectCards/ ProjectCards/

# Рабочая директория — здесь живёт объединённый диспетчер (combined_app.py) и config.yaml
WORKDIR /app/ProjectCards

# Запускаем приложение не от root
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080',timeout=4).status==200 else 1)" || exit 1

CMD ["python", "combined_app.py"]