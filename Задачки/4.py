import threading


def enter(message):
    while True:
        try:
            i = int(input(message))
            return i
        except BaseException:
            print("Неверный ввод!")


def fibonachi(x, res, i):
    if x <= 0:
        return 0
    elif x == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, x):
            a, b = b, a + b
        res[i] = b


def main():
    num_threads = enter("Введите число потоков: ")
    inputs = []

    for i in range(num_threads):
        n = enter(f"Введите число для потока {i + 1}: ")
        inputs.append(n)

    threads = []
    res = [None] * num_threads

    for i in range(num_threads):
        thread = threading.Thread(target=fibonachi, args=(inputs[i], res, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for i in range(num_threads):
        print(f"Число Фибоначчи для {inputs[i]} равно: {res[i]}")


main()
