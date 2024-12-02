import threading
import time


def start_thread(i, lock):
    print(f"Поток {i} запущен")
    time.sleep(2)
    with lock:
        print(f"Поток {i} завершен")


threads = []
lock = threading.Lock()

for i in range(7):
    thread = threading.Thread(target=start_thread, args=(str(i + 1), lock))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("Все потоки завершены")
