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


class Player(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/bd2.png')
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QBrush(pixmap))
        self.cell_size = CELL_SIZE

    def picture(self, direction, move):
        if direction == 0: # up
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bu1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bu2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bu3.png')
        elif direction == 1: #left
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bl1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bl2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bl3.png')
        elif direction == 2: #right
            if move % 4 == 0:
                pixmap = QPixmap(':/image/br1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/br2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/br3.png')
        elif direction == 3: #down
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bd1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bd2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bd3.png')

        pixmap = pixmap.scaled(self.cell_size, self.cell_size)
        self.setBrush(QBrush(pixmap))


class Player2(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/bd2.png')
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QBrush(pixmap))
        self.cell_size = CELL_SIZE

    def picture(self, direction, move):
        if direction == 0: # up
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bu1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bu2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bu3.png')
        elif direction == 1: #left
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bl1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bl2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bl3.png')
        elif direction == 2: #right
            if move % 4 == 0:
                pixmap = QPixmap(':/image/br1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/br2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/br3.png')
        elif direction == 3: #down
            if move % 4 == 0:
                pixmap = QPixmap(':/image/bd1.png')
            elif move % 4 == 1 or move % 4 == 3:
                pixmap = QPixmap(':/image/bd2.png')
            elif move % 4 == 2:
                pixmap = QPixmap(':/image/bd3.png')

        pixmap = pixmap.scaled(self.cell_size, self.cell_size)
        self.setBrush(QBrush(pixmap))


class Enemy1(QGraphicsRectItem):
    def __init__(self, row, col, cords_explode, cords_double_explode, CELL_SIZE, NUM_ROWS, NUM_COLS):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.direction = None
        pixmap = QPixmap(':/image/ed2.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.timer = QTimer()
        self.timer.timeout.connect(self.move)
        self.v = random.randint(1,3)
        self.timer.start(self.v*500)
        self.col = col
        self.row = row
        self.change_direction()
        self.cords_explode = cords_explode
        self.cords_double_explode = cords_double_explode
        self.step = 0
        self.enemy_history = []
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.cell_size = CELL_SIZE

        self.timer_enemy_1_pos = QTimer()
        self.timer_enemy_1_pos.timeout.connect(self.position_enemy)
        self.timer_enemy_1_pos.start(500)

    def move(self):
        self.step += 1
        if self.direction == "right":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/er1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/er2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/er3.png')
            if self.col < (self.num_rows - 2) and self.row % 2 == 1:
                z = (self.row, self.col + 1)
                if not self.check_collision(z):
                    self.moveBy(self.cell_size, 0)
                    self.col += 1
            self.change_direction()

        elif self.direction == "left":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/el1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/el2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/el3.png')
            if self.col >= 2 and self.row % 2 == 1:
                z = (self.row, self.col - 1)
                if not self.check_collision(z):
                    self.moveBy(-self.cell_size, 0)
                    self.col -= 1
            self.change_direction()

        pixmap = pixmap.scaled(self.cell_size, self.cell_size)
        self.setBrush(QBrush(pixmap))

    def change_direction(self):
        self.direction = random.choice(["left", "right"])

    def check_collision(self, z):
        if z in self.cords_explode or z in self.cords_double_explode:
                return True
        return False

    def position_enemy(self):
        pair = (self.col, self.row)
        self.enemy_history.append(pair)


class Enemy2(QGraphicsRectItem):
    def __init__(self, row, col, cords_explode, cords_double_explode, CELL_SIZE, NUM_ROWS, NUM_COLS):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.direction = None
        pixmap = QPixmap(':/image/td2.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.timer = QTimer()
        self.col = col
        self.row = row
        self.step = 0
        self.timer.timeout.connect(self.move)
        self.v = random.randint(1,3)
        self.timer.start(self.v*500)
        self.change_direction()
        self.cords_explode = cords_explode
        self.cords_double_explode = cords_double_explode
        self.enemy_history = []
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.cell_size = CELL_SIZE

        self.timer_enemy_2_pos = QTimer()
        self.timer_enemy_2_pos.timeout.connect(self.position_enemy)
        self.timer_enemy_2_pos.start(500)

    def move(self):
        self.step += 1
        #print(self.col,self.row)
        if self.direction == "down":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/td1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/td2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/td3.png')
            if self.row < (self.num_cols - 2) and self.col % 2 == 1:
                z = (self.row+1, self.col)
                if not self.check_collision(z):
                    self.moveBy(0, self.cell_size)
                    self.row += 1
            self.change_direction()
        elif self.direction == "up":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/tu1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/tu2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/tu3.png')
            if self.row >= 2 and self.col % 2 == 1:
                z = (self.row-1, self.col)
                if not self.check_collision(z):
                    self.moveBy(0, -self.cell_size)
                    self.row -= 1
            self.change_direction()
        elif self.direction == "right":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/tr1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/tr2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/tr3.png')
            if self.col < (self.num_rows - 2) and self.row % 2 == 1:
                z = (self.row, self.col+1)
                if not self.check_collision(z):
                    self.moveBy(self.cell_size, 0)
                    self.col += 1
            self.change_direction()
        elif self.direction == "left":
            if self.step % 4 == 0:
                pixmap = QPixmap(':/image/tl1.png')
            elif self.step % 4 == 1 or self.step % 4 == 3:
                pixmap = QPixmap(':/image/tl2.png')
            elif self.step % 4 == 2:
                pixmap = QPixmap(':/image/tl3.png')
            if self.col >= 2 and self.row % 2 == 1:
                z = (self.row, self.col-1)
                if not self.check_collision(z):
                    self.moveBy(-self.cell_size, 0)
                    self.col -= 1
            self.change_direction()

        pixmap = pixmap.scaled(self.cell_size, self.cell_size)
        self.setBrush(QBrush(pixmap))

    def change_direction(self):
        self.direction = random.choice(["up", "down", "left", "right"])

    def check_collision(self, z):
        if z in self.cords_explode or z in self.cords_double_explode:
            return True
        return False

    def position_enemy(self):
        pair = (self.col, self.row)
        self.enemy_history.append(pair)


class Brick(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/block.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))


class Brick1E(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/brick2.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))


class Brick2E(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/brick1.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))


class Bomb(QGraphicsEllipseItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/bomb.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.col = col
        self.row = row


class Explosion(QGraphicsRectItem):
    def __init__(self, row, col, CELL_SIZE):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/image/fire.png')
        pixmap = pixmap.scaled(CELL_SIZE, CELL_SIZE)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.col = col
        self.row = row