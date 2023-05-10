from PyQt5.QtGui import QBrush, QPixmap, QPen, QIntValidator
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QResource, QRectF
import xml.etree.ElementTree as ET
import sqlite3
import sys
import random
import images_rc
import json
import objects


class Game(QGraphicsView):
    def __init__(self):
        super().__init__()
        WINDOW_WIDTH = CELL_SIZE * NUM_COLS + 40
        WINDOW_HEIGHT = CELL_SIZE * NUM_ROWS + 40
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(Qt.white)

        self.player = objects.Player(1, 1, CELL_SIZE)
        self.scene.addItem(self.player)
        self.player2alive = False
        self.player_online = False
        self.bomb_one = False
        self.bomb_two = False
        self.bricks = []
        self.str = []
        self.no_bricks = []
        self.enemies = []
        self.bombs_on_board = []
        self.cords_explode = []
        self.cords_double_explode = []
        self.cords = []
        self.ruch = 0
        self.ruch2 = 0
        self.player_move_history = []
        self.player_move_history2 = []
        self.player_bomb_history = []

        if GAME_MODE == '2play':
            self.player2 = objects.Player2(NUM_ROWS-2, NUM_COLS-2, CELL_SIZE)
            self.scene.addItem(self.player2)
            self.player2alive = True
        elif GAME_MODE == 'internet':
            print('internet')
            self.player_online = True
            
        else:
            print('one player')

        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                if row == 0 or row == NUM_ROWS - 1 or col == 0 or col == NUM_COLS - 1:
                    brick = objects.Brick(row, col, CELL_SIZE)
                    self.scene.addItem(brick)

        for x in range(1, NUM_ROWS - 1):
            for y in range(1, NUM_COLS - 1):
                if not ((x == 1 and y == 2) or (x == 2 and y == 1) or (x == 1 and y == 1) or (x == (NUM_ROWS - 2) and y == (NUM_COLS - 2)) or
                        (x == (NUM_ROWS - 3) and y == (NUM_COLS - 2)) or (x == (NUM_ROWS - 2) and y == (NUM_COLS - 3))):
                    pair = (x, y)
                    if x % 2 == 0 and y % 2 == 0:
                        brick = objects.Brick(x, y, CELL_SIZE)
                        self.scene.addItem(brick)
                        self.bricks.append(brick)
                        self.str.append(pair)
                        self.cords.append([x, y])
                    elif random.random() < 0.15 and x < NUM_COLS - 1 and y < NUM_COLS - 1:
                        brick = objects.Brick1E(x, y, CELL_SIZE)
                        self.bricks.append(brick)
                        self.scene.addItem(brick)
                        self.str.append(pair)
                        self.cords_explode.append(pair)
                        self.cords.append([x, y])
                    elif random.random() < 0.05 and x < NUM_COLS - 1 and y < NUM_COLS - 1:
                        brick = objects.Brick2E(x, y, CELL_SIZE)
                        self.bricks.append(brick)
                        self.scene.addItem(brick)
                        self.str.append(pair)
                        self.cords_double_explode.append(pair)
                        self.cords.append([x, y])
                    else:
                        self.no_bricks.append(pair)

        for i in range(3):
            z = random.choice(self.no_bricks)
            x, y = z
            enemy = objects.Enemy2(x, y, self.cords_explode, self.cords_double_explode, CELL_SIZE, NUM_ROWS, NUM_COLS)
            self.no_bricks.remove(z)
            self.scene.addItem(enemy)
            self.enemies.append(enemy)

        for i in range(3):
            z = random.choice(self.no_bricks)
            x, y = z
            enemy = objects.Enemy1(x, y, self.cords_explode, self.cords_double_explode, CELL_SIZE, NUM_ROWS, NUM_COLS)
            self.no_bricks.remove(z)
            self.scene.addItem(enemy)
            self.enemies.append(enemy)

        self.timer_enemy = QTimer()
        self.timer_enemy.timeout.connect(self.if_die_from_enemy)
        self.timer_enemy.start(100)

        self.timer_player_pos = QTimer()
        self.timer_player_pos.timeout.connect(self.position_player)
        self.timer_player_pos.start(500)


    def add_explosion(self, bomb):
        row = bomb.row
        col = bomb.col

        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (i == row or j == col) and i > 0 and j > 0 and i != NUM_COLS - 1 and j != NUM_ROWS - 1 \
                        and (i % 2 != 0 or j % 2 != 0):

                    explosion = objects.Explosion(i, j, CELL_SIZE)
                    self.scene.addItem(explosion)
                    if self.player2alive:
                        if self.if_die(explosion, self.player2):
                            self.game_over()
                    if self.if_die(explosion, self.player):
                        self.game_over()

                    QTimer.singleShot(1000, lambda item=explosion: self.scene.removeItem(item))

                    if self.enemy_dies(explosion) != 0:
                        enemy = self.enemy_dies(explosion)
                        QTimer.singleShot(1000, lambda item=enemy: self.scene.removeItem(item))
                        self.enemies.remove(enemy)

                    pair = (i, j)
                    if pair in self.cords_explode:
                        idx = self.str.index(pair)
                        brick_to_remove = self.bricks[idx]
                        QTimer.singleShot(1000, lambda item=brick_to_remove: self.scene.removeItem(item))
                        self.bricks.pop(idx)
                        self.str.pop(idx)
                        self.cords_explode.remove(pair)
                        self.cords.remove([i, j])

                    elif pair in self.cords_double_explode:
                        idx = self.str.index(pair)
                        brick_to_remove = self.bricks[idx]
                        QTimer.singleShot(1000, lambda item=brick_to_remove: self.scene.removeItem(item))
                        self.bricks.pop(idx)
                        self.str.pop(idx)
                        self.cords_double_explode.remove(pair)
                        self.cords.remove([i, j])

                        new_brick = objects.Brick1E(i, j, CELL_SIZE)
                        self.scene.addItem(new_brick)
                        self.bricks.append(new_brick)
                        self.str.append(pair)
                        self.cords_explode.append(pair)
                        self.cords.append([i, j])


    def keyPressEvent(self, event):
        row = int(self.player.y() / CELL_SIZE)
        col = int(self.player.x() / CELL_SIZE)
        x_pos = self.player.pos().x()
        y_pos = self.player.pos().y()
        self.bomb = objects.Bomb(row + 1, col + 1, CELL_SIZE)

        if event.key() == Qt.Key_Left and col >= 1:
            self.player.picture(1, self.ruch)
            if not self.check_collision(x_pos - CELL_SIZE, y_pos, self.player) and \
                    not self.collision_bomb(x_pos - CELL_SIZE, y_pos, self.player):
                self.player.moveBy(-CELL_SIZE, 0)
            self.ruch += 1

        elif event.key() == Qt.Key_Left and col < 1:
            self.player.picture(1, self.ruch)
            self.player.moveBy(CELL_SIZE * NUM_COLS - 3 * CELL_SIZE, 0)
            self.ruch += 1

        elif event.key() == Qt.Key_Right and col < NUM_COLS - 3:
            self.player.picture(2, self.ruch)
            if not self.check_collision(x_pos + CELL_SIZE, y_pos, self.player) and \
                    not self.collision_bomb(x_pos + CELL_SIZE, y_pos, self.player):
                self.player.moveBy(CELL_SIZE, 0)
            self.ruch += 1

        elif event.key() == Qt.Key_Right and col == NUM_COLS - 3:
            self.player.picture(2, self.ruch)
            self.player.moveBy(- CELL_SIZE * NUM_COLS + 3 * CELL_SIZE, 0)
            self.ruch += 1

        elif event.key() == Qt.Key_Up and row >= 1:
            self.player.picture(0, self.ruch)
            if not self.check_collision(x_pos, y_pos - CELL_SIZE, self.player) and \
                    not self.collision_bomb(x_pos, y_pos - CELL_SIZE, self.player):
                self.player.moveBy(0, -CELL_SIZE)
            self.ruch += 1

        elif event.key() == Qt.Key_Up and row < 1:
            self.player.picture(0, self.ruch)
            self.player.moveBy(0, CELL_SIZE * NUM_ROWS - 3 * CELL_SIZE)
            self.ruch += 1

        elif event.key() == Qt.Key_Down and row < NUM_ROWS - 3:
            self.player.picture(3, self.ruch)
            if not self.check_collision(x_pos, y_pos + CELL_SIZE, self.player) and \
                    not self.collision_bomb(x_pos, y_pos + CELL_SIZE, self.player):
                self.player.moveBy(0, CELL_SIZE)
            self.ruch += 1

        elif event.key() == Qt.Key_Down and row == NUM_ROWS - 3:
            self.player.picture(3, self.ruch)
            self.player.moveBy(0, - CELL_SIZE * NUM_ROWS + 3 * CELL_SIZE)
            self.ruch += 1

        elif event.key() == Qt.Key_Space:
            if not self.bomb_one:
                self.bomb_one = True
                self.scene.addItem(self.bomb)
                QTimer.singleShot(500, lambda item=self.bomb: self.bombs_on_board.append(item))
                QTimer.singleShot(2500, lambda item=self.bomb: self.bombs_on_board.remove(item))
                QTimer.singleShot(2500, lambda item=self.bomb: self.scene.removeItem(item))
                QTimer.singleShot(2500, lambda item=self.bomb: self.add_explosion(item))
                QTimer.singleShot(2500, lambda: setattr(self, 'bomb_one', False))

        if self.check_collision(self.player.x(), self.player.y(), self.player) or self.collision_bomb(self.player.x(), self.player.y(), self.player):
            self.player.setPos(x_pos, y_pos)

        if self.player2alive:
            row2 = int(self.player2.y() / CELL_SIZE) + (NUM_ROWS - 3)
            col2 = int(self.player2.x() / CELL_SIZE) + (NUM_COLS - 3)
            x_pos2 = self.player2.pos().x() + (NUM_ROWS - 3) * CELL_SIZE
            y_pos2 = self.player2.pos().y() + (NUM_COLS - 3) * CELL_SIZE
            self.bomb2 = objects.Bomb(row2 + 1, col2 + 1, CELL_SIZE)

            if event.key() == Qt.Key_A and col2 >= 1:
                self.player2.picture(1, self.ruch2)
                if not self.check_collision(x_pos2 - CELL_SIZE, y_pos2, self.player2) and \
                        not self.collision_bomb(x_pos2 - CELL_SIZE, y_pos2, self.player2):
                    self.player2.moveBy(-CELL_SIZE, 0)
                self.ruch2 += 1

            elif event.key() == Qt.Key_A and col2 < 1:
                self.player2.picture(1, self.ruch2)
                self.player2.moveBy(CELL_SIZE * NUM_COLS - 3 * CELL_SIZE, 0)
                self.ruch2 += 1

            elif event.key() == Qt.Key_D and col2 < NUM_COLS - 3:
                self.player2.picture(2, self.ruch2)
                if not self.check_collision(x_pos2 + CELL_SIZE, y_pos2, self.player2) and \
                        not self.collision_bomb(x_pos2 + CELL_SIZE, y_pos2, self.player2):
                    self.player2.moveBy(CELL_SIZE, 0)
                self.ruch2 += 1

            elif event.key() == Qt.Key_D and col2 == NUM_COLS - 3:
                self.player2.picture(2, self.ruch2)
                self.player2.moveBy(- CELL_SIZE * NUM_COLS + 3 * CELL_SIZE, 0)
                self.ruch2 += 1

            elif event.key() == Qt.Key_W and row2 >= 1:
                self.player2.picture(0, self.ruch2)
                if not self.check_collision(x_pos2, y_pos2 - CELL_SIZE, self.player2) and \
                        not self.collision_bomb(x_pos2, y_pos2 - CELL_SIZE, self.player2):
                    self.player2.moveBy(0, -CELL_SIZE)
                self.ruch2 += 1

            elif event.key() == Qt.Key_W and row2 < 1:
                self.player2.picture(0, self.ruch2)
                self.player2.moveBy(0, CELL_SIZE * NUM_ROWS - 3 * CELL_SIZE)
                self.ruch2 += 1

            elif event.key() == Qt.Key_S and row2 < NUM_ROWS - 3:
                self.player2.picture(3, self.ruch2)
                if not self.check_collision(x_pos2, y_pos2 + CELL_SIZE, self.player2) and \
                        not self.collision_bomb(x_pos2, y_pos2 + CELL_SIZE, self.player2):
                    self.player2.moveBy(0, CELL_SIZE)
                self.ruch2 += 1

            elif event.key() == Qt.Key_S and row2 == NUM_ROWS - 3:
                self.player2.picture(3, self.ruch2)
                self.player2.moveBy(0, - CELL_SIZE * NUM_ROWS + 3 * CELL_SIZE)
                self.ruch2 += 1

            elif event.key() == Qt.Key_E:
                if not self.bomb_two:
                    self.bomb_two = True
                    self.scene.addItem(self.bomb2)
                    QTimer.singleShot(500, lambda item=self.bomb2: self.bombs_on_board.append(item))
                    QTimer.singleShot(2500, lambda item=self.bomb2: self.bombs_on_board.remove(item))
                    QTimer.singleShot(2500, lambda item=self.bomb2: self.scene.removeItem(item))
                    QTimer.singleShot(2500, lambda item=self.bomb2: self.add_explosion(item))
                    QTimer.singleShot(2500, lambda: setattr(self, 'bomb_two', False))

            if self.check_collision(self.player2.x(), self.player2.y(), self.player2) or self.collision_bomb(self.player2.x(), self.player2.y(), self.player):
                self.player2.setPos(x_pos2 - (NUM_ROWS - 3) * CELL_SIZE, y_pos2 - (NUM_COLS - 3) * CELL_SIZE)


    def position_player(self):
        row = int(self.player.y() / CELL_SIZE)
        col = int(self.player.x() / CELL_SIZE)
        pos = (col, row)
        #print(pos)
        self.player_move_history.append(pos)

        if self.player2alive:
            row2 = int(self.player2.y() / CELL_SIZE) + (NUM_ROWS - 3)
            col2 = int(self.player2.x() / CELL_SIZE) + (NUM_COLS - 3)
            pos2 = (col2, row2)
            #print(pos2)
            self.player_move_history2.append(pos2)


    def check_collision(self, x, y, player):
        for brick in self.bricks:
            if brick.collidesWithItem(player) and isinstance(brick, Brick) :
                return True
            if brick.collidesWithItem(player) and (isinstance(brick, Brick1E) or isinstance(brick, Brick2E)):
                return True
        return False


    def collision_bomb(self, x, y, player):
        if bool(self.bombs_on_board):
            for bomb in self.bombs_on_board:
                if bomb.collidesWithItem(player):
                    return True
        return False

    @staticmethod
    def if_die(explosion, player):
        if explosion.collidesWithItem(player):
            return True


    def if_die_from_enemy(self):
        for enemy in self.enemies:
            if enemy.collidesWithItem(self.player):
                self.game_over()
            if self.player2alive:
                if enemy.collidesWithItem(self.player2):
                    self.game_over()


    def enemy_dies(self, explosion):
        for enemy in self.enemies:
            if explosion.collidesWithItem(enemy):
                return enemy
        return False


    def save_xml(self):
        gameplay = []

        for i in range(len(self.player_move_history)):
            sec_group = {"sec": i * 0.5, "player1": self.player_move_history[i]}
            if self.player2alive:
                sec_group["player2"] = self.player_move_history2[i]
            gameplay.append(sec_group)

        root = ET.Element("playback")

        for j in gameplay:
            element = ET.SubElement(root, "czas", sek=str(j["sec"]))
            for player1, punkty in j.items():
                if player1 != "sec":
                    ET.SubElement(element, player1).text = str(punkty)

        tree = ET.ElementTree(root)
        tree.write("gameplay.xml")


    def save_sqt(self):
        conn = sqlite3.connect('gameplay.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS playback 
                        (sec FLOAT, player1 TEXT, player2 TEXT)''')

        for i, move in enumerate(self.player_move_history):
            sec = i * 0.5
            player1 = str(move)
            player2 = str(self.player_move_history2[i]) if self.player2alive else None
            cursor.execute('INSERT INTO playback VALUES (?, ?, ?)', (sec, player1, player2))

        conn.commit()
        conn.close()


    def game_over(self):
        #for i in range (6):
        #        print(self.enemies[i].enemy_history)
        reply = QMessageBox.question(self, "Game over", "Game over!", QMessageBox.Ok,
                                     QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            if XML:
                self.save_xml()
            if SQT:
                self.save_sqt()
            QApplication.quit()


    def closeEvent(self, event):
        if XML:
            self.save_xml()
        if SQT:
            self.save_sqt()


class MenuDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Game options')
        self.setGeometry(600, 400, 600, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.game_mode = None
        self.width = None
        self.height = None
        self.ip = None
        self.mask = None
        self.xml = None
        self.sqt = None

        self.group = QGroupBox('Select game mode', self)
        mode = QVBoxLayout(self.group)
        self.one_radio = QRadioButton('1 Player', self.group)
        self.two_radio = QRadioButton('2 Player', self.group)
        self.internet_radio = QRadioButton('Internet Player', self.group)
        mode.addWidget(self.one_radio)
        mode.addWidget(self.two_radio)
        mode.addWidget(self.internet_radio)

        self.input_group = QGroupBox('Enter value from 10 to 80', self)
        valid = QIntValidator(10, 80)
        input_layout = QFormLayout(self.input_group)
        self.width_edit = QLineEdit()
        self.width_edit.setValidator(valid)
        self.height_edit = QLineEdit()
        self.height_edit.setValidator(valid)
        input_layout.addRow('Width:', self.width_edit)
        input_layout.addRow('Height:', self.height_edit)

        self.internet_group = QGroupBox('Enter IP and mask', self)
        internet_layout = QFormLayout(self.internet_group)
        self.ip_address = QLineEdit()
        self.mask = QLineEdit()
        self.ip_address.setInputMask('000.000.000.000;_')
        self.mask.setInputMask('999;_')
        internet_layout.addRow('Ip address:', self.ip_address)
        internet_layout.addRow('Mask:', self.mask)

        self.extension_group = QGroupBox('Chose form of save:', self)
        save_layout = QHBoxLayout(self.extension_group)
        self.file_sqt = QCheckBox('sqlite3')
        self.file_xml = QCheckBox('xml')
        self.file_json = QCheckBox('json')
        save_layout.addWidget(self.file_sqt)
        save_layout.addWidget(self.file_xml)
        save_layout.addWidget(self.file_json)

        self.choose_group = QGroupBox()
        choose_layout = QHBoxLayout(self.choose_group)
        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.ok_clicked)
        load_button = QPushButton('Load', self)
        load_button.clicked.connect(self.load_clicked)
        choose_layout.addWidget(ok_button)
        choose_layout.addWidget(load_button)

        layout = QHBoxLayout()
        layout.addWidget(self.group)
        layout.addWidget(self.input_group)
        layout.addWidget(self.internet_group)

        widget = QWidget()
        widget.setLayout(layout)
        layout2 = QVBoxLayout()
        layout2.addWidget(widget)
        layout2.addWidget(self.extension_group)
        layout2.addWidget(self.choose_group)
        self.setLayout(layout2)


    def ok_clicked(self):
        if self.one_radio.isChecked():
            self.game_mode = '1play'
        elif self.two_radio.isChecked():
            self.game_mode = '2play'
        elif self.internet_radio.isChecked():
            self.game_mode = 'internet'
        else:
            QMessageBox.question(self, "Do it!", "Choose your mode!", QMessageBox.Ok,
                                 QMessageBox.Ok)

        if not bool(self.width_edit.text()) or not bool(self.height_edit.text()):
            QMessageBox.question(self, "Do it!", "Enter dimensions!", QMessageBox.Ok,
                                         QMessageBox.Ok)
        else:
            self.width = int(self.width_edit.text())
            if self.width % 2 == 0:
                self.width += 1
            self.height = int(self.height_edit.text())
            if self.height % 2 == 0:
                self.height += 1
            if self.height < 10 or self.width < 10 or self.width > 80 or self.height > 80:
                QMessageBox.question(self, "Do it!", "Enter values between 10 and 80!", QMessageBox.Ok,
                                     QMessageBox.Ok)
            else:
                if QCheckBox.isChecked(self.file_json):
                    data = {
                        'game mode': self.game_mode,
                        'width': self.width,
                        'height': self.height,
                        'ip' : self.ip_address.text(),
                        'mask' : self.mask.text(),
                        'xml': self.file_xml.isChecked(),
                        'sqlite3': self.file_sqt.isChecked()
                    }
                    filename, _ = QFileDialog.getSaveFileName(self, 'Zapisz plik', '.',
                                                              'Pliki JSON (*.json);;Wszystkie pliki (*.*)')

                    if filename:
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=4)
                if not self.ip_address.text():
                    self.ip = 0
                if not self.mask.text():
                    self.mask = 0
                if QCheckBox.isChecked(self.file_sqt):
                    self.sqt = True
                else:
                    self.sqt = False
                if QCheckBox.isChecked(self.file_xml):
                    self.xml = True
                else:
                    self.xml = False
                self.accept()

    def load_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Wybierz plik', '.',
                                                  'Pliki JSON (*.json);;Wszystkie pliki (*.*)')

        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.game_mode = data['game mode']
                self.width = data['width']
                self.height = data['height']
                self.ip_address = data['ip']
                self.mask = data['mask']
                self.xml = data['xml']
                self.sqt = data['sqlite3']
                #print(self.ip_address)
            self.accept()
            '''
            if self.game_mode == '1play':
                self.one_radio.setChecked(True)
            elif self.game_mode == '2play':
                self.two_radio.setChecked(True)
            elif self.game_mode == 'internet':
                self.internet_radio.setChecked(True)
            self.width_edit.setText(str(self.width))
            self.height_edit.setText(str(self.height))
            self.ip_address.setText(str(self.ip_address))
            self.mask.setText(str(self.mask))
            if self.xml:
                self.file_xml.setChecked(True)
            if self.file_sqt:
                self.file_sqt.setChecked(True)
            '''

    def get_game_mode(self):
        while not self.game_mode or not self.width or not self.height:
            self.exec_()
        return self.game_mode, self.width, self.height, self.sqt , self.xml, self.ip, self.mask


if __name__ == '__main__':

    CELL_SIZE = 32
    app = QApplication(sys.argv)
    menu_dialog = MenuDialog()
    if menu_dialog.exec_() == QDialog.Accepted:
        GAME_MODE, NUM_ROWS, NUM_COLS, SQT, XML, IP_ADDRESS, MASK = menu_dialog.get_game_mode()
        game = Game()
        game.show()

        sys.exit(app.exec_())