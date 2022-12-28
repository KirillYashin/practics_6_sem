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


def build_path_line(_points):
    factor = .25
    path = QtGui.QPainterPath(_points[0])
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
            path.quadTo(cp2, current)
        else:
            # use the control point "cp1" set in the *previous* cycle
            path.cubicTo(cp1, cp2, current)

        rev_source = QtCore.QLineF.fromPolar(target.length() * factor, angle).translated(current)
        cp1 = rev_source.p2()
    return path


def points_generator(centre_x, centre_y, m_size_point):
    points = []
    # m_size_point = 10
    step_angle = 2.0 * math.pi / m_size_point
    min_r, max_r = 0, 0
    if min_r == 0:
        min_r = random.randint(70, 120)
    if max_r == 0:
        max_r = random.randint(120, 170)
    for i in range(m_size_point):
        now_angle = step_angle * i
        r = random.randint(min_r, max_r)
        x_coord = centre_x + int(round(r * math.sin(now_angle)))
        y_coord = centre_y + int(round(r * math.cos(now_angle)))
        new_point = QPoint(x_coord, y_coord)
        points.append(new_point)
    points.append(points[0])
    return points


def points_generator_line(centre_x, centre_y, points_num, rotation):
    _points = list()
    middle = list()
    k = math.tan(math.radians(rotation))
    middle.append(QPoint(centre_x, abs(centre_y)))
    for i in range(1, points_num + 1):
        r_x = random.randint(30, 50)
        r_y = int(k * r_x)
        x_coord_middle = int(middle[i - 1].x()) + int(r_x)
        y_coord_middle = int(int(middle[i - 1].y() + int(r_y)))
        new_point_middle = QPoint(x_coord_middle, y_coord_middle)
        middle.append(new_point_middle)
    for i in range(points_num + 1):
        sign = random.randint(0, 1)
        if not sign:
            sign = -1
        delta = sign * int(random.randint(15, 20))
        _points.append(QPoint(int(middle[i].x() - delta), int(middle[i].y() + delta)))

    return _points


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
        self.angle = 0.0
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
        self.angle = math.atan((self.max_y - self.min_y) / (self.max_x - self.min_x)) * 180 / math.pi
        temp_filled_space = set(itertools.product([x for x in range(self.min_x - 5, self.max_x + 11)],
                                                  [y for y in range(self.min_y - 5, self.max_y + 11)]))
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
        left_upper = QPoint(self.min_x, self.min_y)
        left_lower = QPoint(self.min_x, self.max_y)
        right_upper = QPoint(self.max_x, self.min_y)
        right_lower = QPoint(self.max_x, self.max_y)
        # painter.drawRect(self.min_x, self.min_y, int(self.max_x - self.min_x), int(self.max_y - self.min_y))
        '''painter.drawLine(left_upper, left_lower)
        painter.drawLine(left_lower, right_lower)
        painter.drawLine(right_lower, right_upper)
        painter.drawLine(right_upper, left_upper)'''

        painter = QPainter(self.mask_image)
        painter.setBrush(QBrush(self.light_color))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        painter.setPen(QPen(self.dark_color, 2))
        path.moveTo(self.bounds_points[0])
        painter.drawPath(path)
        self.save_mask_image('mask')
        self.update()

    def draw_line(self, rotation):
        parameter_map = {
            "waviness": 20,
            "length": 3,
            "thickness": 15,
            "border_colour": 135,
            "insides_colour": 155
        }
        x_rand = random.randint(0, int(self.max_x - self.min_x)) + self.min_x
        y_rand = random.randint(0, int(self.max_y - self.min_y)) + self.min_y
        painter = QPainter(self.image)
        points = points_generator_line(x_rand, y_rand, parameter_map["length"], rotation)
        path = build_path_line(points)
        pen = QPen()
        pen.setColor(QColor().fromRgb(parameter_map["border_colour"],
                                      parameter_map["border_colour"],
                                      parameter_map["border_colour"]))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(20)
        painter.setPen(pen)
        painter.drawPath(path)
        self.update()

        pen = QPen()
        pen.setColor(QColor().fromRgb(parameter_map["insides_colour"],
                                      parameter_map["insides_colour"],
                                      parameter_map["insides_colour"]))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(15)
        painter.setPen(pen)
        painter.drawPath(path)
        self.update()

        for x in range(500):
            for y in range(495):
                if self.mask_image.pixelColor(x, y) == Qt.white:
                    painter.setPen(QPen(Qt.white))
                    painter.drawPoint(x, y)
                if self.mask_image.pixelColor(x, y) == self.dark_color:
                    painter.setPen(self.dark_color)
                    painter.drawPoint(x, y)
        self.update()

    def lay_lines_group(self, cnt, common_rotation):
        painter = QPainter(self.image)
        for i in range(cnt):
            self.draw_line(common_rotation)

        '''group_center_x = random.randint(0, int(self.max_x - self.min_x)) + self.min_x
        group_center_y = random.randint(0, int(self.max_y - self.min_y)) + self.min_y
        for i in range(cnt):
            x_rand = random.randint(0, int(self.max_x - self.min_x)) + self.min_x
            y_rand = random.randint(0, int(self.max_y - self.min_y)) + self.min_y
            painter.setPen(QPen(Qt.red, 2))
            painter.drawPoint(x_rand, y_rand)
            directory = os.path.join(os.getcwd(), 'lines')
            file_name = f'line_{i}'
            path = os.path.join(directory, file_name + '.png')
            scale_size_x = random.randint(100, 120)
            scale_size_y = random.randint(200, 220)
            line_pixmap = QPixmap(path).scaled(scale_size_x, scale_size_y)
            rotation = common_rotation + random.randint(0, 15)
            rotated_pixmap = line_pixmap.transformed(QTransform().rotate(rotation),
                                                     Qt.FastTransformation)
            painter.drawPixmap(x_rand - scale_size_x // 2, y_rand - scale_size_y // 2, rotated_pixmap)'''
        '''for x in range(500):
            for y in range(495):
                if self.mask_image.pixelColor(x, y) == Qt.white:
                    painter.setPen(QPen(Qt.white))
                    painter.drawPoint(x, y)
                if self.mask_image.pixelColor(x, y) == self.dark_color:
                    painter.setPen(self.dark_color)
                    painter.drawPoint(x, y)'''
        self.update()
        self.save_image('test')

    def draw_mitochondrion(self, group_cnt, low, middle, high):
        self.draw_mitochondrion_boundaries()
        common_rotation = random.randint(-45, 45)
        for _ in range(group_cnt):
            self.draw_line(common_rotation)
        self.lay_background(low, middle, high)
        self.init_window()

    def save_image(self, name):
        directory = os.getcwd()
        file_name = f'mitochondrion_{name}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            self.image.save(path)

    def save_mask_image(self, name):
        directory = os.getcwd()
        file_name = f'mitochondrion_{name}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            self.mask_image.save(path)

    def save_line_image(self, cnt):
        directory = os.path.join(os.getcwd(), 'lines')
        file_name = f'line_{cnt}'
        if file_name:
            path = os.path.join(directory, file_name + '.png')
            pixmap = QPixmap(self.image)
            pixmap.setMask(pixmap.createHeuristicMask(Qt.transparent))
            pixmap.save(path)

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
    App = QApplication(sys.argv)
    window = Window()
    # dark - 10, 50, 200
    # semi dark - 25, 90, 190
    # semi light - 70, 140, 195
    # light - 130, 150, 195
    window.draw_mitochondrion(5, 10, 50, 200)
    # window.draw_mitochondrion(m_cnt, e_cnt, c_cnt, colors[0], colors[1], colors[2])
    image = cv2.imread('mitochondrion_background.png')
    img_blur = cv2.GaussianBlur(image, (5, 5), 0)
    cv2.imshow('img', img_blur)
    cv2.waitKey(0)
    filename = 'mitochondrion'
    cv2.imwrite(os.path.join(os.getcwd(), filename + '.png'), img_blur)
    sys.exit(App.exec())
