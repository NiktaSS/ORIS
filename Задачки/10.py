import  threading, queue, time, random


class Car(threading.Thread):
    def __init__(self, car_num, parking):
        threading.Thread.__init__(self)
        self.car_num = car_num
        self.parking = parking

    def run(self):
        if self.parking.have_place(car_num=self.car_num):
            time_in = random.randint(2, 7)
            time.sleep(time_in)
            self.parking.leave(car_num=self.car_num)

class Parking:
    def __init__(self, size):
        self.size = size
        self.place = queue.Queue(maxsize=size)

    def have_place(self, car_num):
        print(f'Автомобиль {car_num} пытается заехать на парковку')
        if self.place.full():
            print(f'Парковка полна. Автомобиль {car_num} уезжает')
            return False
        else:
            self.place.put(1)
            print(f'Автомобиль {car_num} заехал на парковку')
            return True

    def leave(self, car_num):
        self.place.get()
        print(f'Автомобиль {car_num} покинул парковку')


def main():
    amount_cars = 10
    parking_size = 3
    parking = Parking(parking_size)

    cars = []

    for i in range(amount_cars):
        car = Car(i+1, parking)
        cars.append(car)

    for car in cars:
        car.start()
        time.sleep(1)

    for car in cars:
        car.join()

main()