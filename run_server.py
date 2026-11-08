from waitress import serve
from api.index import app

if __name__ == '__main__':
    # Запускаем Waitress на порту 5000
    # threads=4 — количество потоков для обработки запросов
    print("Starting server on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000, threads=4)