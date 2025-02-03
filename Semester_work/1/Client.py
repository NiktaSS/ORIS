import pickle
import socket
from threading import Thread
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject, QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QComboBox, QGridLayout
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter
from queue import SimpleQueue
from registrationUI import Ui_RegisterWindow
from GameUI import Ui_GameWindow

class Communication(QObject):
    chat_signal = pyqtSignal(str)
    enter_room_signal = pyqtSignal(str)
    game_signal = pyqtSignal(tuple)
    start_game_signal = pyqtSignal(int)
    timer_signal = pyqtSignal(int)
    end_game_signal = pyqtSignal()
class Registration(QMainWindow, Ui_RegisterWindow):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.setupUi(self)
        self.communication = Communication()
        self.socket_comm = Socket(self.communication)
        self.setWindowTitle("Registration")
        self.registration_enter_line.setPlaceholderText("Your name...")
        self.registration_btn.clicked.connect(self.send_name)
        self.registration_enter_line.returnPressed.connect(self.send_name)

        self.setMinimumSize(QSize(360, 250))
        self.setMaximumSize(QSize(360, 250))

        self.show()
    @pyqtSlot()
    def send_name(self):
        name = self.registration_enter_line.text()
        if not name.isalnum():
            self.registration_text.append("Wrong name!")
            return
        elif name in self.socket_comm.names:
            self.registration_text.append("This name is already taken!")
            return
        self.name = name
        self.socket_comm.queue.put({'type': 'name', 'body': name})
        self.hide()
        self.rooms_window = Rooms(name, self.communication, self.socket_comm)

class Rooms(QWidget):
    def __init__(self, name, communication, socket_comm):
        super().__init__()
        self.name = name
        self.communication = communication
        self.socket_comm = socket_comm
        self.room = ''
        self.color = ''
        self.waiting_room = None
        self.setWindowTitle('Rooms')
        self.layout = QVBoxLayout()
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.room_box = QComboBox()
        self.room_box.addItems( [('Digital Dreamland'), ('Spectrum Showdown'),
                                 ('Pixelated Port'), ('Monochrome Madness'),
                                 ('Vivid Voyage'), ('Grid Galaxy'),
                                 ('Colorful Carnival'), ('Chroma Challenge'),
                                 ('Shade Seekers'), ('Prismatic Playoff')])

        self.color_box = QComboBox()
        self.colors = [
            ('Red', QColor(255, 0, 0)),
            ('Green', QColor(0, 255, 0)),
            ('Blue', QColor(0, 0, 255)),
            ('Yellow', QColor(255, 255, 0)),
            ('Cyan', QColor(0, 255, 255)),
            ('Magenta', QColor(255, 0, 255)),
            ('Orange', QColor(255, 165, 0)),
            ('Purple', QColor(128, 0, 128)),
            ('Pink', QColor(255, 192, 203)),
            ('Black', QColor(0, 0, 0))]
        for color_name, color in self.colors:
            self.color_box.addItem(color_name)
            self.color_box.setItemData(self.color_box.count() - 1, color, role=Qt.ItemDataRole.BackgroundRole)
            text_color = QColor(255, 255, 255) if color.value() < QColor(128, 128, 128).value() else QColor(0, 0, 0)
            self.color_box.setItemData(self.color_box.count() - 1, text_color, role=Qt.ItemDataRole.ForegroundRole)


        self.btn_enter = QPushButton('OK')
        self.btn_enter.clicked.connect(self.check_color)

        self.communication.enter_room_signal.connect(self.enter_to_rooms)

        self.layout.addWidget(self.status)
        self.layout.addWidget(self.room_box)
        self.layout.addWidget(self.color_box)
        self.layout.addWidget(self.btn_enter)
        self.setLayout(self.layout)

        self.setMinimumSize(QSize(260, 260))
        self.setMaximumSize(QSize(260, 260))

        self.show()

    def check_color(self):
        self.socket_comm.queue.put({'type': 'room', 'body': f'{self.room_box.currentText()}\t{self.color_box.currentText()}'})

    def enter_to_rooms(self, body):
        if body == 'error':
            self.status.append('This color is already used in this room!')
        else:
            self.room = self.room_box.currentText()
            self.color = self.color_box.currentText()
            self.hide()
            self.status.setText('')
            self.room_window = Room(self.name, self.communication, self.socket_comm, self)
            if int(body) == 0:
                self.waiting_room = WaitRoom(self.name, self.room_window)

class WaitRoom(QWidget):
    def __init__(self, name, room_window, font_size=25):
        super().__init__()
        self.name = name
        self.room_window = room_window
        self.setWindowTitle("Wait Room")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.name_label = QLabel(f'{self.name}, \nyou are the only player in the room, \nwait for the others...')
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFont(QFont('Arial', font_size))
        self.quit_button = QPushButton("Quit the game")
        self.quit_button.clicked.connect(self.room_window.exit_room)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.quit_button)
        self.setLayout(self.layout)
        self.show()

class Room(QMainWindow, Ui_GameWindow):
    def __init__(self, name, communication, socket_comm, room_menu):
        super().__init__()
        self.setupUi(self)
        self.name = name
        self.communication = communication
        self.socket_comm = socket_comm
        self.room_menu = room_menu
        self.setWindowTitle(self.room_menu.room)
        self.start = False
        self.btn_map = {}
        self.generate_map()
        self.setGeometry(0, 0, 1900, 100)
        self.setMinimumWidth(1900)

        self.communication.game_signal.connect(self.game_updating_logic)
        self.communication.chat_signal.connect(self.update_chat)
        self.communication.start_game_signal.connect(self.start_game)
        self.communication.timer_signal.connect(self.update_timer)
        self.communication.end_game_signal.connect(self.stop_game)

        self.chat_send.clicked.connect(self.chat_sending)
        self.exit_btn.clicked.connect(self.exit_room)
        self.show()

    def generate_map(self):
        self.btn_map.clear()
        self.grid_btn_Layout.setSpacing(0)
        self.grid_btn_Layout.setContentsMargins(0, 0, 0, 0)
        for x in range(20):
            for y in range(30):
                cell = QPushButton()
                cell.setMaximumHeight(50)
                cell.setMinimumHeight(50)
                cell.setMaximumWidth(50)
                cell.setMinimumWidth(50)
                cell.setStyleSheet('border: none; background-color: white;')
                self.grid_btn_Layout.addWidget(cell, x, y)
                self.btn_map[(x, y)] = cell
                cell.clicked.connect(lambda state, X=x, Y=y: self.btn_game_logic(X, Y))

    @pyqtSlot(int)
    def start_game(self, time):
        try:
            print('df')
            if self.room_menu.waiting_room is not None and self.room_menu.waiting_room.isVisible():
                self.room_menu.waiting_room.hide()
            self.label.setText(f'Timer: {time}')
            self.chat_text.append('The game has begun!')
            self.start = True
            #self.show()
        except Exception as e:
            print(e)

    @pyqtSlot(int)
    def update_timer(self, time):
        try:
            self.label.setText(f'Timer: {time}')
        except Exception as e:
            print(f'Timer update error: {e}')

    @pyqtSlot()
    def btn_game_logic(self, x, y):
        if self.start == True:
            self.socket_comm.queue.put({'type': 'btn', 'body': (x, y, self.room_menu.color)})

    @pyqtSlot(tuple)
    def game_updating_logic(self, body):
        x, y, color = body
        cell = self.btn_map[(x, y)]
        cell.setStyleSheet(f'border: none; background-color: {color};')

    @pyqtSlot()
    def chat_sending(self):
        msg = self.chat_enter_line.text()
        if msg != '':
            data = f'{self.name}\t{msg}'
            self.socket_comm.queue.put({'type': 'chat', 'body': data})
            self.chat_text.append(f'[You]: {msg}')
            self.chat_enter_line.setText('')

    @pyqtSlot(str)
    def update_chat(self, data):
        try:
            name, msg = data.split('\t')
            self.chat_text.append(f'[{name}]: {msg}')
        except Exception:
            self.chat_text.append(data)

    @pyqtSlot()
    def exit_room(self):
        if self.room_menu.waiting_room is not None and self.room_menu.waiting_room.isVisible():
            self.room_menu.waiting_room.hide()
        else:
            self.hide()
        self.socket_comm.queue.put({'type': 'exit_room', 'body': None})
        self.room_menu.show()

    @pyqtSlot()
    def stop_game(self):
        self.chat_text.append('The game is over!')
        self.start = False
        self.exit_room()


class Socket:
    def __init__(self, communication):
        self.queue = SimpleQueue()
        self.communication  = communication
        self.names = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 9000))

        Thread(target=self.send, daemon=True).start()
        Thread(target=self.recieve, daemon=True).start()

    def send(self):
        while True:
            data = self.queue.get()
            serialized_data = pickle.dumps(data)
            self.sock.sendall(serialized_data)

    def recieve(self):
        while True:
            try:
                data = self.sock.recv(1024)
                deserialized_data = pickle.loads(data)
                print(deserialized_data)
                if data is None:
                    continue

                type = deserialized_data['type']
                body = deserialized_data['body']

                match type:
                    case 'chat':
                        self.communication.chat_signal.emit(body)
                    case 'names':
                        self.names = body
                    case 'enter':
                        self.communication.enter_room_signal.emit(body)
                    case 'btn':
                        self.communication.game_signal.emit(body)
                    case 'start':
                        print('start')
                        self.communication.start_game_signal.emit(body)
                        print('start')
                    case 'timer':
                        self.communication.timer_signal.emit(body)
                    case 'stop':
                        self.communication.end_game_signal.emit()



            except Exception as e:
                print(f"Error receiving data: {e}")
                break


app = QApplication([])
window = Registration()
app.exec()