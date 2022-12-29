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
import line
import numpy as np


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
    step_angle = 2.0 * math.pi / m_size_point
    min_r, max_r = 0, 0
    if min_r == 0:
        min_r = random.randint(40, 65)
    if max_r == 0:
        max_r = random.randint(65, 95)
    for i in range(m_size_point):
        now_angle = step_angle * i
        r = random.randint(min_r, max_r)
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
        self.center_x, self.center_y = -1, -1
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
        painter = QPainter(self.image)
        '''line.generate_line()
        directory = os.path.join(os.getcwd(), 'lines')
        file_name = f'line_{0}'
        filepath = os.path.join(directory, file_name + '.png')
        line_pixmap = QPixmap(filepath).scaled(250, 250)
        rotation = 0
        rotated_pixmap = line_pixmap.transformed(QTransform().rotate(rotation), Qt.FastTransformation)
        brush = QtGui.QBrush()
        brush.setTexture(rotated_pixmap)
        painter.setBrush(brush)
        painter.drawRect(QRect(QPoint(-1, -1), QPoint(500, 495)))
        self.save_image('12313')'''

        self.center_x = random.randint(25, 475)
        self.center_y = random.randint(25, 475)
        self.bounds_points = points_generator(self.center_x, self.center_y, 10)
        self.max_x, self.max_y = -1, -1
        self.min_x, self.min_y = 501, 496
        for point in self.bounds_points:
            self.max_x = max(self.max_x, point.x())
            self.max_y = max(self.max_y, point.y())
            self.min_x = min(self.min_x, point.x())
            self.min_y = min(self.min_y, point.y())
        temp_filled_space = set(itertools.product([x for x in range(self.min_x - 5, self.max_x + 11)],
                                                  [y for y in range(self.min_y - 5, self.max_y + 11)]))
        if len(self.filled_space.intersection(temp_filled_space)) != 0:
            return
        self.filled_space = self.filled_space.union(temp_filled_space)

        path = build_path(self.bounds_points)
        painter.setBrush(QBrush(self.light_color))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 10))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)

        painter = QPainter(self.mask_image)
        painter.setBrush(QBrush(self.light_color))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 10))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        self.update()

    def lay_lines(self, cnt, common_rotation, common_length):
        painter = QPainter(self.image)
        for i in range(cnt):
            line.generate_line()

        group_center_x = random.randint(0, int(self.max_x - self.min_x)) + self.min_x
        group_center_y = random.randint(0, int(self.max_y - self.min_y)) + self.min_y
        for i in range(cnt):
            # x_rand = random.randint(self.min_x, self.max_x)
            # y_rand = random.randint(self.min_y, self.max_y)
            x_rand = random.randint(group_center_x - 20, group_center_x + 20)
            y_rand = random.randint(group_center_y - 20, group_center_y + 20)
            # print(x_rand, y_rand)
            directory = os.path.join(os.getcwd(), 'lines')
            file_name = f'line_{1}'
            path = os.path.join(directory, file_name + '.png')
            scale_size = random.randint(40, 120)
            # rotation = common_rotation + random.randint(-5, 5)\
            rotation = 0
            line_pixmap = QPixmap(path)
            rotated_pixmap = line_pixmap.transformed(QTransform().rotate(rotation), Qt.FastTransformation)
            painter.drawPixmap(x_rand, y_rand,
                               rotated_pixmap)
        for x in range(500):
            for y in range(495):
                if self.mask_image.pixelColor(x, y) == Qt.white:
                    painter.setPen(QPen(Qt.white))
                    painter.drawPoint(x, y)
                if self.mask_image.pixelColor(x, y) == self.dark_color:
                    painter.setPen(self.dark_color)
                    painter.drawPoint(x, y)
        self.update()
        self.save_image('test')

    def draw_mitochondrion(self, low, middle, high):
        self.draw_mitochondrion_boundaries()
        painter = QPainter(self.image)
        line.generate_line()
        directory = os.path.join(os.getcwd(), 'lines')
        file_name = f'line_{0}'
        path = os.path.join(directory, file_name + '.png')
        rotation = random.randint(0, 90)
        scale_size = 200
        line_pixmap = QPixmap(path).scaled(scale_size, scale_size)
        rotated_pixmap = line_pixmap.transformed(QTransform().rotate(rotation), Qt.FastTransformation)
        painter.drawPixmap(int(self.min_x - 50),
                           int(self.min_y - 50),
                           rotated_pixmap)
        for x in range(500):
            for y in range(495):
                if self.mask_image.pixelColor(x, y) == Qt.white:
                    painter.setPen(QPen(Qt.white))
                    painter.drawPoint(x, y)
                if self.mask_image.pixelColor(x, y) == self.dark_color:
                    painter.setPen(self.dark_color)
                    painter.drawPoint(x, y)
        self.update()
        self.save_image('test')
        self.lay_background(low, middle, high)

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
                if self.mask_image.pixelColor(x, y) == Qt.white:
                    self.image.setPixelColor(x, y, background.pixelColor(x, y))
                '''if self.image.pixelColor(x, y) == self.dark_color:
                    random_color = random.randint(low, middle + 1)
                    color = QColor()
                    color.setRgb(random_color, random_color, random_color)
                    self.image.setPixelColor(x, y, color)
                if self.image.pixelColor(x, y) == self.light_color:
                    random_color = random.randint(middle + 1, high + 1)
                    color = QColor()
                    color.setRgb(random_color, random_color, random_color)
                    self.image.setPixelColor(x, y, color)'''
        self.update()
        self.save_image('background')


if __name__ == '__main__':
    App = QApplication(sys.argv)
    # window = Window()
    # dark - 10, 50, 200
    # semi dark - 25, 90, 190
    # semi light - 70, 140, 195
    # light - 130, 150, 195
    for i in range(50):
        window = Window()
        colours = [0, 0, 0]
        colour_choice = random.randint(0, 3)
        if colour_choice == 0:
            colours = [10, 50, 200]
        if colour_choice == 1:
            colours = [25, 90, 190]
        if colour_choice == 2:
            colours = [70, 140, 195]
        if colour_choice == 3:
            colours = [130, 150, 195]
        window.draw_mitochondrion(colours[0], colours[1], colours[2])
        # window.draw_mitochondrion(m_cnt, e_cnt, c_cnt, colors[0], colors[1], colors[2])
        image = cv2.imread('mitochondrion_background.png')
        img_blur = cv2.GaussianBlur(image, (5, 5), 0)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        height, width = img_gray.shape
        noisy = img_gray + np.random.poisson(np.ones((height, width), np.uint8)) * 15 - 15
        # cv2.imshow('img', img_blur)
        # cv2.waitKey(0)
        filename = os.path.join('examples', f'mitochondrion_{i}')
        cv2.imwrite(os.path.join(os.getcwd(), filename + '.png'), noisy)
        print(f'{i} ready')
    sys.exit(App.exit(0))
