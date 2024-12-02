import threading
import time
def is_prostoe(x):
    for d in range(2, int(x**0.5)+1):
        if x % d == 0:
            return 0
    return 1

def find_prostwoe(start, end, result, i):
    numbers = []
    for num in range(start, end):
        if is_prostoe(num):
            numbers.append(num)
    result[i] = numbers

def main():
    low_limit = 1000
    up_limit = 2_000_000
    quantity_of_threads = 10

    plenty_of_numbers = (up_limit-low_limit) // quantity_of_threads
    threads = []
    result = [None] * quantity_of_threads

    for i in range(quantity_of_threads):
        start = low_limit + i*plenty_of_numbers
        end = low_limit + (i+1)*plenty_of_numbers if i!=quantity_of_threads-1 else up_limit+1
        thread = threading.Thread(target=find_prostwoe, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    res = []
    for i in result:
        if i is not None:
            res.extend(i)
    print(len(res))
t1 = time.time()
main()
t2 = time.time()
print(t2-t1)