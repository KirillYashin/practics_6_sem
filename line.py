import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import random
import math


def points_generator(centre_x, centre_y, points_num):
    _points = list()
    middle = list()
    k = 1
    # _points.append(QPoint(centre_x, int(k * centre_y)))
    middle.append(QPoint(centre_x, int(k * centre_y)))
    for i in range(1, points_num + 1):
        r_x = random.randint(30, 50)
        r_y = random.randint(30, 50)
        x_coord_middle = int(middle[i - 1].x()) + int(r_x)
        y_coord_middle = int(k * (int(middle[i - 1].y()) + int(r_y)))
        new_point_middle = QPoint(x_coord_middle, y_coord_middle)
        middle.append(new_point_middle)
    for i in range(points_num + 1):
        sign = random.randint(0, 1)
        if not sign:
            sign = -1
        # sign = (-1) ** i
        delta = sign * int(random.randint(20, 40) * math.cos(math.pi / 4))
        _points.append(QPoint(int(middle[i].x() - delta), int(middle[i].y() + delta)))
    return _points


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Mitochondrion"
        self.width = 300
        self.height = 300
        self.top = 150
        self.left = 150
        self.size = QSize(300, 300)
        self.path = None
        self.image = QImage(self.size, QImage.Format_RGB32)
        self.image.fill(Qt.white)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        # self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QRect(0, 0, self.width, self.height), self.image)

    def build_path(self, _points):
        # points, points_under = points_generator(100, 100, 5)
        factor = .25
        self.path = QtGui.QPainterPath(_points[0])
        cp1 = None
        for p, current in enumerate(_points[1:-1], 1):
            # previous segment
            source = QtCore.QLineF(_points[p - 1], current)
            # next segment
            target = QtCore.QLineF(current, _points[p + 1])
            target_angle = target.angleTo(source)
            if target_angle > 180:
                angle = (source.angle() + source.angleTo(target) / 2) % 360
            else:
                angle = (target.angle() + target.angleTo(source) / 2) % 360

            rev_target = QtCore.QLineF.fromPolar(source.length() * factor, angle + 180).translated(current)
            cp2 = rev_target.p2()

            if p == 1:
                self.path.quadTo(cp2, current)
            else:
                # use the control point "cp1" set in the *previous* cycle
                self.path.cubicTo(cp1, cp2, current)

            rev_source = QtCore.QLineF.fromPolar(target.length() * factor, angle).translated(current)
            cp1 = rev_source.p2()

        # the final curve, that joins to the last point
        # self.path.quadTo(cp1, points[-1])

    def draw(self, cnt):
        # self.image.fill(Qt.white)
        painter = QPainter(self.image)
        pen = QPen()
        pen.setColor(QColor().fromRgb(135, 135, 135))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(50)
        painter.setPen(pen)
        painter.drawPath(self.path)
        self.update()

        pen = QPen()
        pen.setColor(QColor().fromRgb(155, 155, 155))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(20)
        painter.setPen(pen)
        painter.drawPath(self.path)
        self.update()

        self.init_window()
        self.save_image(cnt)

    def save_image(self, cnt):
        directory = os.path.join(os.getcwd(), 'lines')
        file_name = f'line_{cnt}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            # scaled_image = self.image.scaled(50, 50)
            pixmap = QPixmap(self.image)
            pixmap.setMask(pixmap.createHeuristicMask(Qt.transparent))
            pixmap.save(path)


def generate_line(cnt):
    # app = QApplication(sys.argv)
    window = Window()
    points = points_generator(70, 70, 4)
    window.build_path(points)
    window.draw(cnt)

    # sys.exit(app.exit(0))
