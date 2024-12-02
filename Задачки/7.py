import threading
import re


def preparing(text):
    return re.findall(r"\w+", text.lower())


def work(fragment, res, i):
    d = {x: fragment.count(x) for x in set(fragment)}
    res[i] = d


def main():
    file = open("7.txt", "r")
    text = file.read()
    file.close()
    num_threads = 2
    threads = []
    res = [{} for _ in range(num_threads)]

    text = preparing(text)
    ln_fr = len(text) // num_threads

    for i in range(num_threads):
        start = i * ln_fr
        end = (i + 1) * ln_fr if i != num_threads - 1 else len(text)
        thread = threading.Thread(target=work, args=(text[start:end], res, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    result = {}
    for i in range(num_threads):
        for a, b in res[i].items():
            if a in result:
                result[a] += b
            else:
                result[a] = b

    for a, b in result.items():
        print(f"{a}:{b}")


main()
