from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import hmtai
import random
import time
import requests # request img from web
import shutil # save img locally
p = 0
IMG_BOMB = QImage("./images/bomb.png")
IMG_FLAG = QImage("./images/flag.png")
IMG_CLOCK = QImage("./images/bomb.png")

def a():
    url = hmtai.get("hmtai", "neko") 
    file_name = "zxc.png"
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ',url)
        return "zxc.png"
    else:
        a()
    

NUM_COLORS = {
    1: QColor('#f44336'),
    2: QColor('#9C27B0'),
    3: QColor('#3F51B5'),
    4: QColor('#03A9F4'),
    5: QColor('#00BCD4'),
    6: QColor('#4CAF50'),
    7: QColor('#E91E63'),
    8: QColor('#FF9800')
}

LEVELS = [
    (8, 10),
    (16, 40),
    (24, 99)
]

STATUS_READY = 0
STATUS_PLAYING = 1
STATUS_FAILED = 2
STATUS_SUCCESS = 3

STATUS_ICONS = {
    STATUS_READY: "./images/bomb.png",
    STATUS_PLAYING: "./images/bomb.png",
    STATUS_FAILED: "./images/bomb.png",
    STATUS_SUCCESS: "./images/bomb.png",
}


class Pos(QWidget):
    expandable = pyqtSignal(int, int)
    clicked = pyqtSignal()
    ohno = pyqtSignal()
    
    def __init__(self, x, y, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)
        
        

        self.x = x
        self.y = y
    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap("./images/smiley-lol.png")
        painter.drawPixmap(self.rect(), pixmap)
        #painter.setPen((QPen(QColor("green"))))
        #painter.drawEllipse(100, 100, 30, 30)
    def reset(self):
        self.is_start = False
        self.is_mine = False
        self.adjacent_n = 0

        self.is_revealed = False
        self.is_flagged = False

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setRenderHint(QPainter.Antialiasing)

        r = event.rect()
        if self.is_revealed == False:
            outer, inner = Qt.gray, Qt.lightGray
            p.fillRect(r, QBrush(inner))
            pen = QPen(outer)
            pen.setWidth(1)
            p.setPen(pen)
            p.drawRect(r)
        if self.is_revealed:
            """color = self.palette().color(QPalette.Background)
            outer, inner = color, color
            p.fillRect(r, QBrush(inner))
            pen = QPen(outer)
            pen.setWidth(0)
            p.setPen(pen)
            p.drawRect(r)"""
            
            if self.is_revealed:
                if self.is_start:
                    p.setPen(Qt.NoPen)
                    #p.drawPixmap(r, QPixmap(IMG_START))

                elif self.is_mine:
                    p.drawPixmap(r, QPixmap(IMG_BOMB))

                elif self.adjacent_n > 0:
                    pen = QPen(NUM_COLORS[self.adjacent_n])
                    p.setPen(pen)
                    f = p.font()
                    f.setBold(True)
                    p.setFont(f)
                    p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, str(self.adjacent_n))
                elif self.adjacent_n == 0:
                    p.setPen(Qt.NoPen)
        else:
            pass
            """color = self.palette().color(QPalette.Background)
            outer, inner = color, color
            p.fillRect(r, QBrush(inner))
            pen = QPen(outer)
            pen.setWidth(0)
            p.setPen(pen)"""
            
        
        

        if self.is_flagged:
            p.drawPixmap(r, QPixmap(IMG_FLAG))

    def flag(self):
        self.is_flagged = True
        self.update()

        self.clicked.emit()

    def reveal(self):
        self.is_revealed = True
        self.update()

    def click(self):
        if not self.is_revealed:
            self.reveal()
            if self.adjacent_n == 0:
                #self.expandable.emit(self.x, self.y)
                pass
                

        self.clicked.emit()

    def mouseReleaseEvent(self, e):
        
        if (e.button() == Qt.RightButton and self.is_flagged == True):
            self.is_flagged = False
            self.update()
        elif (e.button() == Qt.RightButton and not self.is_revealed):
            self.flag()
        elif (e.button() == Qt.LeftButton):
            if (e.button() == Qt.LeftButton and self.is_flagged == True):
                pass
            else:
                self.click()
                if self.is_mine:
                    self.ohno.emit()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.b_size, self.n_mines = LEVELS[1]
        self.w = QWidget()
        hb = QHBoxLayout()
        #BG1 = QHBoxLayout()
        self.mines = QLabel()
        self.mines.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        f = self.mines.font()
        f.setPointSize(24)
        f.setWeight(75)
        self.mines.setFont(f)
        self.clock.setFont(f)

        self._timer = QTimer()
        self._timer.timeout.connect(self.update_timer)
        self._timer.start(1000)  # 1 second timer

        self.mines.setText("%03d" % self.n_mines)
        self.clock.setText("000")

        self.button = QPushButton()
        self.button.setFixedSize(QSize(32, 32))
        self.button.setIconSize(QSize(32, 32))
        self.button.setIcon(QIcon("./images/bomb.png"))
        self.button.setFlat(True)

        self.button.pressed.connect(self.button_pressed)
        #hb.addWidget(l)
        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_BOMB))
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hb.addWidget(l)

        hb.addWidget(self.mines)
        hb.addWidget(self.button)
        hb.addWidget(self.clock)

        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_CLOCK))
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hb.addWidget(l)

        vb = QVBoxLayout()
        self.lba = QLabel(self)
        pixmap = QPixmap(QImage(IMG_BG))
        self.lba.setPixmap(pixmap)
        if pixmap.width() >1900:
            b = 1900
        else:
            b = pixmap.width()
        if pixmap.height()>1000:
            a = 1000
        else:
            a = pixmap.height()
        self.w.setFixedSize(QSize(b,a))
        """w.setFixedWidth(pixmap.width())
        w.setFixedHeight(pixmap.height())"""

        self.lba.setAlignment(Qt.AlignVCenter)
        self.lba.resize(pixmap.width(),pixmap.width())
        self.lba.setPixmap(pixmap)
        #hb.addWidget(l)
        self.lba.move(0, 0)

        

        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        vb.addLayout(self.grid)
        self.w.setLayout(vb)
        self.setCentralWidget(self.w)

        self.init_map()
        self.update_status(STATUS_READY)

        self.reset_map()
        self.update_status(STATUS_READY)
        
        self.show()
        
    def init_map(self):
        # Add positions to the map
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = Pos(x, y)
                self.grid.addWidget(w, y, x)
                # Connect signal to handle expansion.
                w.clicked.connect(self.trigger_start)
                w.expandable.connect(self.expand_reveal)
                w.ohno.connect(self.game_over)

    def reset_map(self):
        # Clear all mine positions
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reset()

        # Add mines to the positions
        positions = []
        while len(positions) < self.n_mines:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_mine = True
                positions.append((x, y))

        def get_adjacency_n(x, y):
            positions = self.get_surrounding(x, y)
            n_mines = sum(1 if w.is_mine else 0 for w in positions)

            return n_mines

        # Add adjacencies to the positions
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.adjacent_n = get_adjacency_n(x, y)

        # Place starting marker
        while True:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            w = self.grid.itemAtPosition(y, x).widget()
            # We don't want to start on a mine.
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_start = True

                # Reveal all positions around this, if they are not mines either.
                for w in self.get_surrounding(x, y):
                    if not w.is_mine:
                        w.click()
                break

    def get_surrounding(self, x, y):
        positions = []

        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                positions.append(self.grid.itemAtPosition(yi, xi).widget())

        return positions

    def button_pressed(self):
        pass

    def reveal_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reveal()

    def expand_reveal(self, x, y):
        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                w = self.grid.itemAtPosition(yi, xi).widget()
                if not w.is_mine:
                    w.click()

    def trigger_start(self, *args):
        if self.status != STATUS_PLAYING:
            # First click.
            self.update_status(STATUS_PLAYING)
            # Start timer.
            self._timer_start_nsecs = int(time.time())

    def update_status(self, status):
        self.status = status
        self.button.setIcon(QIcon(STATUS_ICONS[self.status]))

    def update_timer(self):
        if self.status == STATUS_PLAYING:
            n_secs = int(time.time()) - self._timer_start_nsecs
            self.clock.setText("%03d" % n_secs)

    def game_over(self):
        self.reveal_map()
        self.update_status(STATUS_FAILED)

    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_W:
            self.update_status(STATUS_FAILED)
            self.reveal_map()
        if event.key() == Qt.Key_R:
            lpixmap = QPixmap(QImage(a()))
            
            if lpixmap.width() >1900:
                b = 1900
            else:
                b = lpixmap.width()
            if lpixmap.height()>1000:
                ah = 1000
            else:
                ah = lpixmap.height()
            self.setFixedSize(QSize(b,ah))
            self.w.setFixedSize(b,ah)
            self.lba.resize(b,ah)
            self.lba.setPixmap(lpixmap)
            self.lba.move(0, 0)
            self.update_status(STATUS_READY)
            self.reset_map()

        if event.key() == Qt.Key_Q:
            app.exec_()
        event.accept()    





if __name__ == '__main__':
    app = QApplication([])
    IMG_BG = QImage(a())
    window = MainWindow()
    app.exec_()
    