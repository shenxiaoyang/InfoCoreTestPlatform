# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import socket
import re

from InfoCoreTestPlatformBaseUI import BaseDlg1
from InfoCoreTools.WindowsCMD import pingIP

logger = logging.getLogger('root.IometerResultHandlerTool.IometerResultHandlerToolUI')

class IometerResultHandlerDlg(BaseDlg1):
    sin1 = pyqtSignal()
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(IometerResultHandlerDlg, self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('Iometer结果处理')  # 设置窗口标题
        self.csv_num = 2

        # 布局参数
        self.horizontalLayout1_width = 700
        self.horizontalLayout2_width = 50
        self.horizontalLayout1_heigth = 25
        self.horizontalLayoutWidget = {}
        self.horizontalLayout = {}
        self.label_file_path = {}
        self.lineEdit_file_path = {}
        self.btn_choose_file = {}
        self.set_ui()

    def set_ui(self):
        for i in range(self.csv_num):
            self.horizontalLayoutWidget[i] = QWidget(self)
            self.horizontalLayout[i] = QHBoxLayout(self.horizontalLayoutWidget[i])
            self.horizontalLayout[i].setContentsMargins(0, 0, 0, 0)

            self.label_file_path[i] = QLabel(self)
            self.label_file_path[i].setText('csv{}路径:'.format(i+1))
            self.horizontalLayout[i].addWidget(self.label_file_path[i])

            self.lineEdit_file_path[i] = QLineEdit(self)
            self.horizontalLayout[i].addWidget(self.lineEdit_file_path[i])

            self.btn_choose_file[i] = QPushButton(self)
            self.btn_choose_file[i].setText('选择')
            self.horizontalLayout[i].addWidget(self.btn_choose_file[i])
        self.horizontalLayoutWidget2 = QWidget(self)
        self.horizontalLayout2 = QHBoxLayout(self.horizontalLayoutWidget2)
        self.horizontalLayout2.setContentsMargins(0, 0, 0, 0)

        self.btn_add_file = QPushButton(self)
        self.btn_add_file.setText('+')
        self.horizontalLayout2.addWidget(self.btn_add_file)

        self.btn_remove_file = QPushButton(self)
        self.btn_remove_file.setText('-')
        self.horizontalLayout2.addWidget(self.btn_remove_file)

        self.btn_get_result = QPushButton(self)
        self.btn_get_result.setText('处理csv')

        self.set_layout()

    def set_layout(self):
        for i in range(self.csv_num):
            self.horizontalLayoutWidget[i].setGeometry(QRect(self.x_left_margin_10,
                                                             self.y_up_margin_10 + i * self.horizontalLayout1_heigth,
                                                             self.horizontalLayout1_width,
                                                             self.horizontalLayout1_heigth))

        x = self.csv_num - 1
        self.horizontalLayoutWidget2.setGeometry(QRect(2 * self.x_left_margin_10 + self.horizontalLayout1_width,
                                                       self.y_up_margin_10 + x * self.horizontalLayout1_heigth,
                                                       self.horizontalLayout2_width,
                                                       self.horizontalLayout1_heigth))

        self.btn_get_result.setGeometry(QRect(
            2 * self.x_left_margin_10 + self.horizontalLayout1_width + self.horizontalLayout2_width - self.button_width_60,
            2 * self.y_up_margin_10 + self.csv_num * self.horizontalLayout1_heigth,
            self.button_width_60,
            self.button_height_25))

        self.resize(3 * self.x_left_margin_10 + self.horizontalLayout1_width + self.horizontalLayout2_width,
                    3 * self.y_up_margin_10 + (self.csv_num + 1) * self.horizontalLayout1_heigth)  # 设置窗口大小


    def connect_all_signal_slot(self):
        self.btn_add_file.clicked.connect(self.btn_add_file_clicked)
        self.btn_remove_file.clicked.connect(self.btn_remove_file_clicked)
        self.btn_get_result.clicked.connect(self.btn_get_result_clicked)
        #下面是个很蠢的办法........
        for i in range(self.csv_num):
            if i == 0:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(0))
            if i == 1:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(1))
            if i == 2:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(2))
            if i == 3:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(3))
            if i == 4:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(4))
            if i == 5:
                self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(5))

    def btn_get_result_clicked(self):
        pass


    def btn_choose_file_clicked(self,num):
        open = QFileDialog()
        self.open_path = open.getOpenFileName()
        self.path = self.open_path[0]
        self.lineEdit_file_path[num].setText(self.path)

    def btn_remove_file_clicked(self):
        self.csv_num = self.csv_num - 1
        self.horizontalLayoutWidget[self.csv_num].close()
        self.set_layout()

    def btn_add_file_clicked(self):
        self.csv_num = self.csv_num + 1
        i = self.csv_num - 1
        self.horizontalLayoutWidget[i] = QWidget(self)
        self.horizontalLayout[i] = QHBoxLayout(self.horizontalLayoutWidget[i])
        self.horizontalLayout[i].setContentsMargins(0, 0, 0, 0)

        self.label_file_path[i] = QLabel(self)
        self.label_file_path[i].setText('csv{}路径:'.format(i + 1))
        self.horizontalLayout[i].addWidget(self.label_file_path[i])

        self.lineEdit_file_path[i] = QLineEdit(self)
        self.horizontalLayout[i].addWidget(self.lineEdit_file_path[i])

        self.btn_choose_file[i] = QPushButton(self)
        self.btn_choose_file[i].setText('选择')
        self.horizontalLayout[i].addWidget(self.btn_choose_file[i])
        self.btn_choose_file[i].clicked.connect(lambda: self.btn_choose_file_clicked(i))

        self.horizontalLayoutWidget[i].show()

        self.set_layout()





