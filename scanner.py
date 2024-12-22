# ИСАДИЧЕВА ДАРЬЯ АЛЕКСЕЕВНА, ДПИ22-1

import socket  # сокеты
import threading  # для многопоточности
from tqdm import tqdm  # для progress bar

# проверяем хост/IP-адрес
# если пользователь вводит хост - идёт проверка и возвращается IP-адрес
# если пользователь вводит IP - функция вернет этот же IP-адрес без изменений
# в случае некорректного имени хоста/IP-адреса - False

def is_valid_host(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

# функция для соединения с портами
def port_connect(ip, port, open_ports):
    try:
        # создаём сокет
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # таймаут на подключение к порту (если порт недоступен/не отвечает)
        s.settimeout(1)
        try:
            # подключение к порту
            connect = s.connect_ex((ip, port))
            # если подключение успешно - добавляем порт в список открытых портов
            # и выводим сообщение
            if connect == 0:
                open_ports.append(port)
        # закрываем сокет
        finally:
            s.close()
    except:
        pass

# функция для сканирования портов по порядку
def sequential_scan(host):
    # список открытых портов
    open_ports = []
    try:
        ip = socket.gethostbyname(host)
        print("\n=== Последовательная обработка ===")
        print(f"Сканируем по порядку порты {ip}...")
        # сканируем порты 0 - 65535
        with tqdm(total=65536, desc="Сканирование") as pbar:
            for port in range(0, 65536):
                port_connect(ip, port, open_ports)
                pbar.update(1)  # Обновляем прогресс-бар
    # обрабатываем ошибки
    except socket.error as e:
        print(f"Ошибка: {e}")
    # останавливаем сканер вручную
    except KeyboardInterrupt:
        print("Сканирование портов было прервано.")
    if not open_ports:
        print("Свободные порты не найдены.")
    # возвращаем список открытых портов
    return sorted(open_ports)

# функция для параллельного сканирования портов
def parallel_scan(host):
    # список открытых портов
    open_ports = []
    try:
        ip = socket.gethostbyname(host)
        print("\n=== Параллельная обработка ===")
        print(f"Сканируем параллельно порты {ip}...")
        # список всех потоков
        threads = []
        # для каждого порта создаём и запускаем поток, добавляем их в список потоков
        with tqdm(total=65536, desc="Сканирование") as pbar:
            for port in range(0, 65536):
                thread = threading.Thread(target=lambda: [port_connect(ip, port, open_ports), pbar.update(1)])
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        # завершение потоков
        for thread in threads:
            thread.join()
    # обрабатываем ошибки
    except socket.error as e:
        print(f"Ошибка: {e}")
    # останавливаем сканирование вручную
    except KeyboardInterrupt:
        print("Сканироание портов было прервано.")
    if not open_ports:
        print("Свободные порты не найдены.")
    # возвращаем список открытых портов
    return sorted(open_ports)

# предлагаем пользователю ввести имя хоста/IP-адрес
if __name__ == "__main__":
    while True:
        host = input("Введите имя хоста/IP-адрес: ")
        if is_valid_host(host):
            break
        else:
            print("Некорректное имя хоста/IP-адрес. Попробуйте снова.")

    # предлагаем метод сканирования портов
    print("\nВыберите метод сканирования:")
    print("1. Последовательное сканирование")
    print("2. Параллельное сканирование")

    # сканирование в зависимости от выбранного метода и вывод списка портов
    while True:
        method = input("Введите номер метода сканирования (1 или 2): ")
        if method == "1":
            open_ports = sequential_scan(host)
            break
        elif method == "2":
            open_ports = parallel_scan(host)
            break
        else:
            print("Некорректный выбор. Введите 1 или 2.")
    if open_ports:
        print("\nОткрытые порты:")
        for port in open_ports:
            print(f" - Порт {port} открыт...")
        print("\nОткрытые порты:", sorted(open_ports))
    else:
        print("Свободные порты не найдены.")
