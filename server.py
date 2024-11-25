import socket  # Модуль для работы с сокетами
import threading  # Модуль для работы с потоками
import sys    # Модуль для доступа к некоторым функциям и переменным интерпретатора Python
import signal  # Модуль для обработки сигналов (например, Ctrl+C)

def client_handler(conn, addr):
    """
    Функция для обработки взаимодействия с клиентом в отдельном потоке.
    """
    print(f"Подключен клиент {addr}")
    try:
        while True:
            # Бесконечный цикл для приема данных от клиента
            data = conn.recv(1024)
            # Получаем данные размером до 1024 байт
            if not data:
                # Если данных нет, значит клиент отключился
                break
            msg = data.decode()
            # Декодируем байтовые данные в строку
            print(f"Получено сообщение от {addr}: {msg}")
            conn.send(data)
            # Отправляем данные обратно клиенту (эхо)
    except ConnectionResetError:
        # Обработка ситуации, когда клиент неожиданно отключился
        print(f"Соединение с клиентом {addr} было разорвано")
    finally:
        print(f"Клиент {addr} отключился")
        conn.close()
        # Закрываем соединение с данным клиентом

def main():
    sock = socket.socket()
    # Создаем TCP-сокет
    # Устанавливаем опцию SO_REUSEADDR, чтобы переиспользовать адрес и порт
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', 9090))
    # Связываем сокет с адресом и портом.
    # Пустая строка '' означает, что сервер будет принимать запросы с любых сетевых интерфейсов.
    sock.listen()
    # Переводим сокет в режим прослушивания входящих подключений
    print("Сервер запущен и ожидает подключений...")

    # Список для хранения активных потоков
    threads = []

    # Обработчик сигнала для корректного завершения сервера при нажатии Ctrl+C
    def signal_handler(sig, frame):
        print("\nЗавершение сервера...")
        sock.close()
        # Закрываем основной сокет, чтобы остановить accept()
        for t in threads:
            t.join()
            # Ждем завершения всех потоков
        sys.exit(0)

    # Регистрируем обработчик сигнала SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            try:
                conn, addr = sock.accept()
                # Принимаем новое входящее подключение
                client_thread = threading.Thread(target=client_handler, args=(conn, addr))
                # Создаем новый поток для обслуживания клиента
                client_thread.start()
                # Запускаем поток
                threads.append(client_thread)
                # Добавляем поток в список активных потоков
            except OSError:
                # Если сокет был закрыт, выходим из цикла
                break
    finally:
        print("Сервер был остановлен.")

if __name__ == "__main__":
    main()
