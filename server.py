# ИСАДИЧЕВА ДАРЬЯ АЛЕКСЕЕВНА, ДПИ22-1

# Код сервера

import socket  # сокеты
import threading  # для многопоточности
import errno  # символические коды ошибок

# счётчик клиентов
client_counter = 0
# объект блокировки для синхронизации доступа к стандартному выводу
print_lock = threading.Lock()
# создаем объект события для остановки сервера
# я решила установить для остановки сервера KeyboardInterrupt чтобы сервер
# не отключался после отключение последнего клиента (чтобы клиенты еще могли подключаться)
shutdown_event = threading.Event()
# список активных соединений
active_connections = []

# работа с клиентом
def client_work(conn, addr):
    global active_connections
    # счётчик клиентов
    global client_counter
    # подключение клиентов
    with print_lock:
        client_counter += 1
        client_number = client_counter
        print(f"Клиент {client_number} {addr} подключился к серверу.")
    # добавляем соединение в список активных соединений
    active_connections.append(conn)
    # принимаем сообщение от клиента порционно
    while not shutdown_event.is_set():
        try:
            data = conn.recv(1024)
            if not data:
                break
            with print_lock:
                print(f"Сервер получил данные от клиента {client_number}: {data.decode()}")
            # немного видоизменим возвращаемые данные
            changed_data = f"{data.decode().replace(' ', '...')}..."
            # отправляем данные клиенту
            conn.send(changed_data.encode())
            with print_lock:
                print(f"Полученые данные были видоизменены и отправлены обратно клиенту {client_number}.")
        except OSError as e:
            if e.errno == errno.EBADF:  # проверяем, что ошибка связана с некорректным файловым дескриптором
                break  # завершаем цикл, если файловый дескриптор некорректен
            else:
                raise  # передаем другие ошибки дальше

    # закрываем соединение
    with print_lock:
        print(f"Отключение клиента {client_number} от сервера...")
        conn.close()
        print(f"Клиент {client_number} отключился от сервера.")
    # удаляем соединение из списка активных соединений
    active_connections.remove(conn)

# создание сервера
def my_server():
    # устанавливаем хост (пустая строка) и порт (0-65535)
    host = ''
    port = 56362

    # создаём сокет
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # привязка сокета к хосту и порту
        server_socket.bind((host, port))
        # прослушивание
        # 5 - максимальное количество ожидающих подключений в очереди
        # сли в данный момент уже принято максимальное количество подключений,
        # новые запросы будут помещены в очередь ожидания и обработаны после
        # того как одно из подключений будет обработано и закрыто
        server_socket.listen(5)
        with print_lock:
            print(f"Сервер запущен на порту {port}. Для остановки сервера используйте KeyboardInterrupt.")  # служебное сообщение 1
            print(f"Прослушивание порта {port}...")

        # принимаем подключения вплоть до KeyboardInterrupt
        while not shutdown_event.is_set():
            # принимаем подключение клиента
            conn, addr = server_socket.accept()
            # создаём новый поток для обработки клиента
            thread_name = f"поток_{client_counter + 1} "
            client_thread = threading.Thread(target=client_work, name=thread_name, args=(conn, addr))
            # запускаем поток
            client_thread.start()
            with print_lock:
                print(f"Создан новый поток для обработки клиента {addr}. Название потока: {thread_name}")


if __name__ == "__main__":
    try:
        my_server()
    except KeyboardInterrupt:
        shutdown_event.set()
        # закрываем все активные соединения
        for conn in active_connections:
            conn.close()
        with print_lock:
            print("Все активные соединения закрыты.")
        # сокет закрывается автоматически при выходе из блока with
        with print_lock:
            print("Остановка сервера...")
            print("Сервер остановлен.")
