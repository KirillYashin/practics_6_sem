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
        r_x = random.randint(20, 30)
        r_y = random.randint(4, 6)
        x_coord_middle = int(middle[i - 1].x()) + int(r_x)
        y_coord_middle = int(k * (int(middle[i - 1].y())))
        new_point_middle = QPoint(x_coord_middle, y_coord_middle)
        middle.append(new_point_middle)
    for i in range(points_num + 1):
        sign = random.randint(0, 1)
        if not sign:
            sign = -1
        # sign = (-1) ** i
        delta = sign * int(random.randint(4, 9))
        _points.append(QPoint(int(middle[i].x() - delta), int(middle[i].y() - delta)))
    return _points


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Mitochondrion"
        self.width = 500
        self.height = 500
        self.top = 150
        self.left = 150
        self.size = QSize(500, 500)
        self.path = None
        self.image = QImage(self.size, QImage.Format_RGB32)
        self.cropped_image = None
        self.image.fill(QColor().fromRgb(155, 155, 155))

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
        width = random.randint(22, 28)
        painter = QPainter(self.image)
        pen = QPen()
        pen.setColor(QColor().fromRgb(135, 135, 135))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(width)
        painter.setPen(pen)
        painter.drawPath(self.path)
        self.update()

        pen = QPen()
        pen.setColor(QColor().fromRgb(195, 195, 195))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(width - random.randint(12, 16))
        painter.setPen(pen)
        painter.drawPath(self.path)
        self.update()

        self.init_window()
        # self.crop_image()
        self.save_image(cnt)

    def save_image(self, cnt):
        directory = os.path.join(os.getcwd(), 'lines')
        file_name = f'line_{cnt}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            # scaled_image = self.image.scaled(50, 50)
            pixmap = QPixmap(self.image)
            # pixmap.setMask(pixmap.createHeuristicMask(Qt.transparent))
            pixmap.save(path)

    def crop_image(self):
        max_x, max_y = -1, -1
        min_x, min_y = 201, 201
        for x in range(200):
            for y in range(200):
                if self.image.pixelColor(x, y) == QColor().fromRgb(135, 135, 135):
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
        rect = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y))
        self.cropped_image = self.image.copy(rect)
        return max_x, max_y, min_x, min_y


def generate_line():
    window = Window()
    offset = 15
    points_x = []
    points_y = []
    for j in range(8):
        '''for i in range(3):
            points_x.append(random.randint(i * (500 // 3) + 10, (i + 1) * (500 // 3) - offset))'''
        points_x.append(random.randint(20, 40))
        points_x.append(random.randint(135, 155))
        points_x.append(random.randint(260, 280))
        points_x.append(random.randint(385, 405))
        for i in range(4):
            points_y.append(random.randint(j * (500 // 8) + 20, (j + 1) * (500 // 8) - 20))
    '''points_x = random.sample([k for k in range(0, 300)], 50)
    points_y = random.sample([k for k in range(0, 300)], 50)
    coord = set()
    for i in range(50):
        coord.add((points_x[i], points_y[i]))
    print(len(coord))'''
    for i in range(32):
        # points_y = random.sample([k for k in range(0 + 50 * i, 50 * (i + 1), 5)], 70)
        points = points_generator(points_x[i], points_y[i], random.randint(2, 4))
        window.build_path(points)
        window.draw(0)


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    offset = 15
    points_x = []
    points_y = []
    for j in range(8):
        '''for i in range(3):
            points_x.append(random.randint(i * (500 // 3) + 10, (i + 1) * (500 // 3) - offset))'''
        points_x.append(random.randint(20, 40))
        points_x.append(random.randint(135, 155))
        points_x.append(random.randint(260, 280))
        points_x.append(random.randint(385, 405))
        for i in range(4):
            points_y.append(random.randint(j * (500 // 8) + 20, (j + 1) * (500 // 8) - 20))
    print(points_x)
    print(points_y)
    '''points_x = random.sample([k for k in range(0, 300)], 50)
    points_y = random.sample([k for k in range(0, 300)], 50)
    coord = set()
    for i in range(50):
        coord.add((points_x[i], points_y[i]))
    print(len(coord))'''
    for i in range(32):
        # points_y = random.sample([k for k in range(0 + 50 * i, 50 * (i + 1), 5)], 70)
        points = points_generator(points_x[i], points_y[i], random.randint(2, 4))
        window.build_path(points)
        window.draw(0)

    sys.exit(App.exit(0))
