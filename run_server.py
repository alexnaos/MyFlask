from waitress import serve

from api.index import app

if __name__ == '__main__':
    # Запускаем Waitress на всех сетевых интерфейсах
    # host='0.0.0.0' делает сервер доступным по локальному IP (192.168.1.56)
    # threads=4 — количество потоков для обработки запросов
    print("Starting server on http://0.0.0.0:5000 (доступен по IP 192.168.1.56)")
    serve(app, host='0.0.0.0', port=8080, threads=4)