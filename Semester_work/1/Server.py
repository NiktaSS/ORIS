import socket
import pickle
import threading
import time
from threading import Thread
from queue import SimpleQueue
from time import sleep
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor

class Server(Thread):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 9000))
        self.sock.listen(5)
        self.start()
        print('Server is running...')

        self.rooms = {
            'Digital Dreamland': Room('Digital Dreamland'),
            'Spectrum Showdown': Room('Spectrum Showdown'),
            'Pixelated Port': Room('Pixelated Port'),
            'Monochrome Madness': Room('Monochrome Madness'),
            'Vivid Voyage': Room('Vivid Voyage'),
            'Grid Galaxy': Room('Grid Galaxy'),
            'Colorful Carnival': Room('Colorful Carnival'),
            'Chroma Challenge': Room('Chroma Challenge'),
            'Shade Seekers': Room('Shade Seekers'),
            'Prismatic Playoff': Room('Prismatic Playoff')
        }

        self.names = {}

    def run(self):
        while True:
            client_socket, client_addr = self.sock.accept()
            print(f"Client has connected: {client_addr}")
            client_thread = ClientThread(client_socket, client_addr, self.rooms, self)
            client_thread.send({'type': 'names', 'body': list(self.names.values())})

class ClientThread(Thread):
    def __init__(self, sock, addr, rooms, server):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.rooms = rooms
        self.server = server
        self.name = ''
        self.room = None
        self.color = ''
        self.start()

    def run(self):
        try:
            while True:
                data = self.recieve()
                print(data)
                if not data:
                    break
                match data['type']:
                    case 'name':
                        self.name = data['body']
                        self.server.names[self] = self.name
                        self.send({'type': 'chat', 'body': f"Welcome, {self.name}!"})
                    case 'room':
                        self.check_room(data['body'])
                    case 'btn':
                        self.room.update_field_state(data['body'])
                        self.room.broadcast(data)
                    case 'chat':
                        self.room.broadcast(data, self)
                    case 'exit_room':
                        self.room.remove_client(self)
        finally:
            pass
            #self.disconnect()

    def send(self, data):
        try:
            serialized_data = pickle.dumps(data)
            self.sock.sendall(serialized_data)
        except Exception as e:
            print(f"Error sending to client {self.addr}: {e}")
            self.disconnect()

    def recieve(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if data is None:
                    continue
                deserialized_data = pickle.loads(data)
                return deserialized_data

            except Exception as e:
                print(f"Error receiving data from the client {self.addr}: {e}")
                break

    def check_room(self, data):
        try:
            room, color = data.split("\t")
            if color in self.rooms[room].colors:
                self.send({'type': 'enter', 'body': 'error'})
            else:
                self.send({'type': 'enter', 'body': str(len(self.rooms[room].clients))})
                self.room = self.rooms[room]
                self.color = color
                self.room.add_client(self, self.name, self.color)
        except Exception as e:
            print(f"Error checking room for client {self.addr}: {e}")

    def disconnect(self):
        print(f"Client {self.addr} has disconnected.")
        if self.room:
            self.room.remove_client(self)


class Room:
    def __init__(self, name):
        self.name = name
        self.start = False
        self.clients = []
        self.client_data = {} # name:color
        self.colors = set()
        self.field_state = {}
        self.timer = None
        self.game_time = 10

    def generate_field(self):
        for x in range(20):
            for y in range(30):
                self.field_state[(x, y)] = 'white'


    def add_client(self, client, name, color):
        self.clients.append(client)
        self.client_data[client] = {'name': name, 'color': color}
        self.colors.add(color)
        if len(self.clients) > 1:
            self.start_game()

    def remove_client(self, client):
        if client not in self.clients:
            print(f"Client {client} is not in the room.")
            return
        else:
            name = self.client_data[client]['name']
            self.colors.remove(self.client_data[client]['color'])
            del self.client_data[client]
            self.clients.remove(client)
            self.broadcast({'type': 'chat', 'body': f'{name} left the game!'}, client)
            if len(self.clients) < 2:
                self.stop_game(client)
    def broadcast(self, message, curr_client = None):
        for client in self.clients:
            if client != curr_client:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"Error when sending a message to the client: {e}")

    def update_field_state(self, body):
        x, y, color = body
        self.field_state[x, y] = color


    def start_game(self):
        self.generate_field()
        self.timer = Timer(self.game_time, self)
        self.broadcast({'type': 'start', 'body': self.game_time})
        self.timer.start()

    def stop_game(self, client=None):
        self.broadcast({'type': 'stop', 'body': self.game_time}, client)
        image = self.generate_image()
        image.save('field_image.png')

    def generate_image(self):
        width = 30
        height = 20
        pixel_size = 20
        pixmap = QPixmap(width * pixel_size, height * pixel_size)
        painter = QPainter(pixmap)
        for (y, x), color in self.field_state.items():
            painter.fillRect(x * pixel_size, y * pixel_size, pixel_size, pixel_size, QColor(color))
        painter.end()
        return pixmap

class Timer(Thread):
    def __init__(self, time, room):
        super().__init__(daemon=True)
        self.time = time
        self.room = room

    def run(self):
        i = self.time - 1
        while i != -1:
            self.room.broadcast({'type': 'timer', 'body': i})
            time.sleep(1)
            i -= 1
        self.room.stop_game()





server = Server()
app = QApplication([])
app.exec()