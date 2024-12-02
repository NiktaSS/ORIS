import os
import threading
from queue import Queue


def search_files(directory, search, results, lock):
    try:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path):
                search_files(full_path, search, results, lock)
            elif search in entry:
                with lock:
                    results.append(full_path)
    except PermissionError:
        print(f"Нет доступа к каталогу: {directory}")


def worker(queue, search, results, lock):
    while not queue.empty():
        directory = queue.get()
        search_files(directory, search, results, lock)
        queue.task_done()


def main(directories, search, amount_threads):
    results = []
    lock = threading.Lock()
    queue = Queue()

    for directory in directories:
        queue.put(directory)

    threads = []
    for _ in range(min(amount_threads, queue.qsize())):
        thread = threading.Thread(target=worker, args=(queue, search, results, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("Найденные файлы:")
    for result in results:
        print(result)


directories_to_search = ['C:\питон\Practice\AiSD_practice', 'C:\питон\Practice\ОРИС']
search = '.txt'
amount_threads = 4

main(directories_to_search, search, amount_threads)
