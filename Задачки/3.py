import threading


def partial_factorial(start, end, res, index):
    curr = 1
    for i in range(start, end + 1):
        curr *= i
    res[index] = curr


def main():
    num = 15
    quantity_of_threads = 3
    if num < 0:
        return "Факториал не определен для отрицательных чисел!"
    if num in [0, 1]:
        return 1

    result = [1] * quantity_of_threads
    threads = []

    n_range = num // quantity_of_threads

    for i in range(quantity_of_threads):
        start = 1 + i * n_range
        end = (i + 1) * n_range if i != quantity_of_threads - 1 else num
        thread = threading.Thread(target=partial_factorial, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    final_res = 1
    for i in result:
        final_res *= i

    return final_res


print(main())
