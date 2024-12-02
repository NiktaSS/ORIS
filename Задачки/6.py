import threading
import random
import time


class ATM():
    def __init__(self, cash):
        self.cash = cash
        self.lock = threading.Lock()

    def debiting_funds(self, amount):
        with self.lock:
            if amount > self.cash:
                print(f"Недостаточно средств для снятия {amount}. Текущий баланс: {self.cash}. Ожидание...")
                return False
            else:
                self.cash -= amount
                print(f"Снятие успешно! Остаток на счете: {self.cash}.")
                return True


def client(atm, i):
    for _ in range(3):
        amount = random.randint(25, 90)
        print(f"Клиент №{i} пытается списать {amount} рублей")
        flag = atm.debiting_funds(amount)
        if not flag: time.sleep(1)


def main():
    number_of_clients = 4
    cash = 500
    atm = ATM(cash)
    threads = []

    for i in range(number_of_clients):
        thread = threading.Thread(target=client, args=(atm, i + 1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


main()
