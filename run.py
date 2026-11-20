#!/usr/bin/env python3
"""
Простой скрипт для запуска Flask-приложения на локальном сервере.
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.index import app

if __name__ == "__main__":
    print("Запуск Flask-приложения...")
    print("Сайт будет доступен по адресу: http://127.0.0.1:8080")
    print("Для остановки нажмите Ctrl+C")
    app.run(host="127.0.0.1", port=8080, debug=True)