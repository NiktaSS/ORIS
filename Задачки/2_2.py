import time


def is_prostoe(x):
    for d in range(2, int(x ** 0.5) + 1):
        if x % d == 0:
            return 0
    return 1


t1 = time.time()
res = []
for i in range(1000, 2_000_001):
    if is_prostoe(i):
        res.append(i)
print(len(res))
t2 = time.time()
print(t2 - t1)
