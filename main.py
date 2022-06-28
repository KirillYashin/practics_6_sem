import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import random
import math
import itertools
import cv2


def build_path(points):
    factor = .25
    path = QtGui.QPainterPath(points[0])
    cp1 = None
    for p, current in enumerate(points[1:-1], 1):
        # previous segment
        source = QtCore.QLineF(points[p - 1], current)
        # next segment
        target = QtCore.QLineF(current, points[p + 1])
        target_angle = target.angleTo(source)
        if target_angle > 180:
            angle = (source.angle() + source.angleTo(target) / 2) % 360
        else:
            angle = (target.angle() + target.angleTo(source) / 2) % 360
        rev_target = QtCore.QLineF.fromPolar(source.length() * factor, angle + 180).translated(current)
        cp2 = rev_target.p2()
        if p == 1:
            path.quadTo(cp2, current)
        else:
            # use the control point "cp1" set in the *previous* cycle
            path.cubicTo(cp1, cp2, current)
        rev_source = QtCore.QLineF.fromPolar(target.length() * factor, angle).translated(current)
        cp1 = rev_source.p2()
    # the final curve, that joins to the last point
    path.quadTo(cp1, points[-1])
    return path


def points_generator(centre_x, centre_y, m_size_point):
    points = list()
    # m_size_point = 10
    step_angle = 2.0 * math.pi / m_size_point
    min_r, max_r = 0, 0
    if min_r == 0:
        min_r = random.randint(20, 35)
    if max_r == 0:
        max_r = random.randint(35, 65)
    for i in range(m_size_point):
        now_angle = step_angle * i
        r = random.randint(min_r, max_r)
        x_coord = centre_x + int(round(r * math.sin(now_angle)))
        y_coord = centre_y + int(round(r * math.cos(now_angle)))
        new_point = QPoint(x_coord, y_coord)
        points.append(new_point)
    points.append(points[0])
    return points


def points_generator_inside(centre_x, centre_y):
    points = list()
    m_size_point = 5
    step_angle = 2.0 * math.pi / m_size_point
    temp = []
    for i in range(5):
        temp.append(random.randint(1, 10))
    temp = sorted(temp[:3]) + sorted(temp[3:], reverse=True)
    for i in range(m_size_point):
        now_angle = step_angle * i
        r = temp[i]
        x_coord = centre_x + int(round(r * math.sin(now_angle)))
        y_coord = centre_y + int(round(r * math.cos(now_angle)))
        new_point = QPoint(x_coord, y_coord)
        points.append(new_point)
    points.append(points[0])
    return points


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Mitochondrion"
        self.top = 150
        self.left = 150
        self.width = 500
        self.height = 495
        self.bounds_points = None
        self.size = QSize(500, 495)
        self.image = QImage(self.size, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.mask_image = QImage(self.size, QImage.Format_RGB32)
        self.mask_image.fill(Qt.white)
        self.filled_space = set()
        self.max_x, self.max_y = -1, -1
        self.min_x, self.min_y = 501, 496
        self.full_dark_color = QColor().fromRgb(10, 10, 10)
        self.dark_color = QColor().fromRgb(135, 135, 135)
        self.light_color = QColor().fromRgb(155, 155, 155)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QRect(0, 0, self.width, self.height), self.image)

    def draw_mitochondrion_boundaries(self):
        self.bounds_points = points_generator(random.randint(25, 475), random.randint(25, 475), 10)
        self.max_x, self.max_y = -1, -1
        self.min_x, self.min_y = 501, 496
        for point in self.bounds_points:
            self.max_x = max(self.max_x, point.x())
            self.max_y = max(self.max_y, point.y())
            self.min_x = min(self.min_x, point.x())
            self.min_y = min(self.min_y, point.y())
        temp_filled_space = set(itertools.product([x for x in range(self.min_x - 5, self.max_x + 11)],
                                                  [y for y in range(self.min_y - 5, self.max_y + 11)]))
        # print(temp_filled_space)
        if len(self.filled_space.intersection(temp_filled_space)) != 0:
            return
        self.filled_space = self.filled_space.union(temp_filled_space)

        painter = QPainter(self.image)
        path = build_path(self.bounds_points)
        painter.setBrush(QBrush(self.light_color))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 2))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        # uncomment for double line
        '''painter.setPen(QPen(self.light_color, 4))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 2))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)'''

        painter = QPainter(self.mask_image)
        painter.setBrush(QBrush(self.light_color))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 2))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        # uncomment for double line
        '''painter.setPen(QPen(self.light_color, 4))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 2))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)'''
        self.update()

    def draw_mitochondrion_insides(self, cnt_dots, cnt_circles):
        painter = QPainter(self.image)
        for _ in range(cnt_circles):
            x_rand = random.randint(self.min_x - 5, self.max_x + 11)
            y_rand = random.randint(self.min_y - 5, self.max_y + 11)
            points = points_generator_inside(x_rand, y_rand)
            random_thickness = random.randint(1, 2)
            painter.setPen(QPen(self.dark_color, random_thickness))
            path = build_path(points)
            painter.drawPath(path)
        '''for _ in range(cnt_lines):
            x_rand = random.randint(self.min_x - 5, self.max_x + 11)
            y_rand = random.randint(self.min_y - 5, self.max_y + 11)
            points = points_generator(x_rand, y_rand, 10)
            points.append(points[0])
            path = build_path(points)
            random_thickness = random.randint(1, 2)
            painter.setPen(QPen(self.dark_color, random_thickness))
            path.moveTo(points[0])
            painter.drawPath(path)'''
        for _ in range(cnt_dots):
            x_rand = random.randint(self.min_x + 10, self.max_x - 11)
            y_rand = random.randint(self.min_y + 10, self.max_y - 11)
            brush = QBrush(Qt.SolidPattern)
            brush.setColor(self.dark_color)
            painter.setBrush(brush)
            length = random.randint(8, 13)
            width = random.randint(2, 4)
            if random.randint(0, 1):
                painter.drawEllipse(x_rand, y_rand, length, width)
            else:
                painter.drawEllipse(x_rand, y_rand, width, length)
        for x in range(500):
            for y in range(495):
                if self.mask_image.pixelColor(x, y) == Qt.white and self.image.pixelColor(x, y) == self.dark_color:
                    painter.setPen(QPen(Qt.white))
                    painter.drawPoint(x, y)
        self.update()
        self.save_image('no_background')

    def draw_mitochondrion(self, cnt, dots_cnt, curves_cnt, low, middle, high):
        for _ in range(cnt):
            self.draw_mitochondrion_boundaries()
            self.draw_mitochondrion_insides(dots_cnt, curves_cnt)
        self.lay_background(low, middle, high)
        self.init_window()

    def save_image(self, name):
        directory = os.getcwd()
        file_name = f'mitochondrion_{name}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            self.image.save(path)

    def lay_background(self, low, middle, high):
        background = QImage('background.jpg')
        for x in range(500):
            for y in range(495):
                if self.image.pixelColor(x, y) == Qt.white:
                    self.image.setPixelColor(x, y, background.pixelColor(x, y))
                if self.image.pixelColor(x, y) == self.dark_color:
                    random_color = random.randint(low, middle + 1)
                    color = QColor()
                    color.setRgb(random_color, random_color, random_color)
                    self.image.setPixelColor(x, y, color)
                if self.image.pixelColor(x, y) == self.light_color:
                    random_color = random.randint(middle + 1, high + 1)
                    color = QColor()
                    color.setRgb(random_color, random_color, random_color)
                    self.image.setPixelColor(x, y, color)
        self.update()
        self.save_image('background')


if __name__ == '__main__':
    '''print('Enter the amount of mitochondrion')
    m_cnt = int(input())
    print('Enter the amount of ellipses inside')
    e_cnt = int(input())
    print('Enter the amount of curves inside')
    c_cnt = int(input())
    print('Choose mode (1 - dark, 2 - semi dark, 3 - semi light, 4 - light)')
    mode = int(input())
    if mode == 1:
        colors = [10, 50, 200]
    elif mode == 2:
        colors = [25, 90, 190]
    elif mode == 3:
        colors = [70, 140, 195]
    else:
        colors = [130, 150, 195]'''
    App = QApplication(sys.argv)
    window = Window()
    # dark - 10, 50, 200
    # semi dark - 25, 90, 190
    # semi light - 70, 140, 195
    # light - 130, 150, 195
    window.draw_mitochondrion(1, 5, 60, 10, 50, 200)
    # window.draw_mitochondrion(m_cnt, e_cnt, c_cnt, colors[0], colors[1], colors[2])
    image = cv2.imread('mitochondrion_background.png')
    img_blur = cv2.GaussianBlur(image, (5, 5), 0)
    cv2.imshow('img', img_blur)
    cv2.waitKey(0)
    filename = 'mitochondrion'
    cv2.imwrite(os.path.join(os.getcwd(), filename + '.png'), img_blur)
    sys.exit(App.exec())
