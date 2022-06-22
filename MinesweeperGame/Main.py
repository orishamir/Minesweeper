import sys
from random import randint

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QLabel, QPushButton

from PyQt5.QtWidgets import QApplication, QMainWindow

with open("locked_tile.png", 'rb') as f:
    imLocked = f.read()
lockedTileImg = QImage.fromData(imLocked)

with open("flagged_tile.png", 'rb') as f:
    imFlagged = f.read()
flaggedTileImg = QImage.fromData(imFlagged)

with open("tiles_bomb.png", 'rb') as f:
    imBomb = f.read()
bombTileImg = QImage.fromData(imBomb)

with open("0.png", 'rb') as f:
    zeroB = f.read()
zeroBombsImg = QImage.fromData(zeroB)

tileSize = 30
rows = 16
cols = 30

class Game(QMainWindow):
    tiles = []
    def __init__(self):
        super(Game, self).__init__()
        self.setWindowTitle("Minesweeper")
        self.setGeometry(200, 200, cols*tileSize, 50+rows*tileSize)
        self.initUI()
        self.initTiles()
        self.initBombs()
        self.setNearbyAmounts()

    def initUI(self):
        deadLbl = QLabel(self)
        deadLbl.setGeometry(200, 5, 500, 40)
        deadLbl.setText("")
        deadLbl.setFont(QFont('Arial', 20, 5))

        restartBtn = QPushButton(self)
        restartBtn.setGeometry(self.width()//2-50, 0, 100, 40)
        restartBtn.setText("RESTART")
        restartBtn.clicked.connect(self._restart)

        self.deadLbl = deadLbl
        self.restartBtn = restartBtn

    def _restart(self):
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[i])):
                self.tiles[i][j].setPixmap(QPixmap.fromImage(lockedTileImg.scaled(tileSize, tileSize)))
                self.tiles[i][j].nearbyAmount = 0
                self.tiles[i][j].unlocked = False
                self.tiles[i][j].flagged = False
                self.tiles[i][j].isBomb = False

        self.initBombs()
        self.setNearbyAmounts()
        self.deadLbl.setText('')

    def initTiles(self):
        self.tiles = []
        for i in range(0, self.height()-2*tileSize, tileSize):
            self.tiles.append([])
            for j in range(0, self.width(), tileSize):
                t = Tile(self)
                t.setGeometry(j, 50+i, tileSize, tileSize)
                t.setPixmap(QPixmap.fromImage(lockedTileImg.scaled(tileSize, tileSize)))
                self.tiles[-1].append(t)

    def initBombs(self):
        bombsAmount = 90  # easy=10, intermediate=40, expert=99
        bombsPositions = []
        while bombsAmount != 0:
            while (pos := [randint(0, rows-1), randint(0, cols-1)]) in bombsPositions:
                continue
            bombsPositions.append(pos)
            bombsAmount -= 1
        self.bombPositions = bombsPositions
        for pos in bombsPositions:
            t = self.tiles[pos[0]][pos[1]]
            # t.setPixmap(QPixmap.fromImage(bombTileImg.scaled(tileSize, tileSize)))
            t.isBomb = True

    def setNearbyAmounts(self):
        tiles = self.tiles
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                n = self.countBombsNearby(i, j)
                self.tiles[i][j].nearbyAmount = n

    def countBombsNearby(self, i, j):
        tiles = self.tiles

        if tiles[i][j].isBomb:
            return
        n = 0
        if i != 0:
            if j != 0:
                n += tiles[i-1][j - 1].isBomb
            n += tiles[i - 1][j].isBomb
            if j != len(tiles[i])-1:
                n += tiles[i - 1][j + 1].isBomb

        if j != 0:
            n += tiles[i][j - 1].isBomb
        # n += tiles[i][j].isBomb
        if j != len(tiles[i])-1:
            n += tiles[i][j + 1].isBomb

        if i != len(tiles)-1:
            if j != 0:
                n += tiles[i+1][j-1].isBomb
            n += tiles[i + 1][j].isBomb
            if j != len(tiles[i])-1:
                n += tiles[i+1][j+1].isBomb
        return n

    def dead(self):
        self.deadLbl.setText("Oh you ded.")

        for pos in self.bombPositions:
            t = self.tiles[pos[0]][pos[1]]
            t.setPixmap(QPixmap.fromImage(bombTileImg.scaled(tileSize, tileSize)))

    def unlock(self, i, j):
        tiles = self.tiles
        if tiles[i][j].unlocked:
            return
        tiles[i][j]._unlock()

        if self.allNeighborsUnlocked(i, j) or tiles[i][j].nearbyAmount != 0 or tiles[i][j].isBomb:
            return

        if i != 0:
            if j != 0:
                self.unlock(i - 1, j - 1)
            self.unlock(i - 1, j)
            if j != len(tiles[i]) - 1:
                self.unlock(i - 1, j + 1)

        if j != 0:
            self.unlock(i, j - 1)
        # n += tiles[i][j].isBomb
        if j != len(tiles[i]) - 1:
            self.unlock(i, j + 1)

        if i != len(tiles) - 1:
            if j != 0:
                self.unlock(i+1, j - 1)
            self.unlock(i+1, j)
            if j != len(tiles[i]) - 1:
                self.unlock(i+1, j + 1)

        if self.checkIfWon():
            self.deadLbl.setText("WON EZ GG")

    def allNeighborsUnlocked(self, i, j):
        tiles = self.tiles
        n = 0
        if i != 0:
            if j != 0:
                n += tiles[i - 1][j - 1].unlocked
            n += tiles[i - 1][j].unlocked
            if j != len(tiles[i])-1:
                n += tiles[i - 1][j + 1].unlocked

        if j != 0:
            n += tiles[i][j - 1].unlocked
        # n += tiles[i][j].isBomb
        if j != len(tiles[i])-1:
            n += tiles[i][j + 1].unlocked

        if i != len(tiles)-1:
            if j != 0:
                n += tiles[i + 1][j - 1].unlocked
            n += tiles[i + 1][j].unlocked
            if j != len(tiles[i])-1:
                n += tiles[i + 1][j + 1].unlocked

        if i == 0 or i == len(tiles)-1:
            if j == 0:
                return n == 3
            else:
                return n == 5
        elif j == 0 or j == len(tiles[i])-1:
            return n == 5
        else:
            return n == 8

    def checkIfWon(self):
        return (any(not self.tiles[pos[0]][pos[1]].flagged for pos in self.bombPositions) and
                all(self.tiles[i][j].unlocked for i in range(len(self.tiles)) for j in range(len(self.tiles[i]))))

class Tile(QLabel):
    unlocked = False
    flagged = False
    isBomb = False
    nearbyAmount = 0

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        if ev.button() == Qt.RightButton:
            if not self.unlocked:
                self.flaggedChanged()
        elif ev.button() == Qt.LeftButton:
            if not self.flagged:
                self.window().unlock(self.y()//tileSize-1, self.x()//tileSize)

    def flaggedChanged(self):
        self.flagged = not self.flagged
        if self.flagged:
            self.setPixmap(QPixmap.fromImage(flaggedTileImg.scaled(tileSize, tileSize)))
        else:
            self.setPixmap(QPixmap.fromImage(lockedTileImg.scaled(tileSize, tileSize)))

    def _unlock(self):
        if self.unlocked:
            return
        self.unlocked = True
        if self.isBomb:
            self.setPixmap(QPixmap.fromImage(bombTileImg.scaled(tileSize, tileSize)))
            self.window().dead()
        else:
            n = self.nearbyAmount
            with open(f"{n}.png", 'rb') as f:
                im = f.read()
            tileImg = QImage.fromData(im)
            self.setPixmap(QPixmap.fromImage(tileImg.scaled(tileSize, tileSize)))


app = QApplication(sys.argv)

game = Game()
game.show()
app.exec_()
