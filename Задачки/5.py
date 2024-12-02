import random
import threading
from random import randint

def sorting(data, res, index):
    res[index] = sorted(data)

def unification(data1, data2):
    i, j = 0, 0
    result = []
    while i < len(data1) and j < len(data2):
        if data1[i] < data2[j]:
            result.append(data1[i])
            i+=1
        else:
            result.append(data2[j])
            j+=1
    if j == len(data2):
        result.extend(data1[i:])
    else:
        result.extend(data2[j:])
    return result

def main(num_threads, data):
    threads = []
    res = [None]*num_threads
    lenth = len(data)//num_threads

    for i in range(num_threads):
        start = i*lenth
        end = (i+1) * lenth if i!=num_threads - 1 else len(data) + 1
        thread = threading.Thread(target=sorting, args=(data[start:end], res, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    sorted_array = res[0]
    for array in res[1:]:
        sorted_array = unification(sorted_array, array)

    return sorted_array

num_threads = 2
data = [random.randint(0, 1000) for _ in range(1000)]

print(main(num_threads, data)==sorted(data))