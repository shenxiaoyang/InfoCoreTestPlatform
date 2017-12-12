# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import socket
import re

from InfoCoreTestPlatformBaseUI import BaseDlg1
from InfoCoreTools.WindowsCMD import pingIP

logger = logging.getLogger('root.PortTestTool.PortTestToolUI')

class PortScanToolDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(PortScanToolDlg, self).__init__(parent)

    def init_ui(self):
        self.resize(350, 60)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.setWindowTitle('端口扫描')  # 设置窗口标题

        self.horizontalLayoutWidget1 = QWidget(self)
        self.horizontalLayoutWidget1.setGeometry(QRect(0, 0, 170, 60))
        self.horizontalLayout1 = QHBoxLayout(self.horizontalLayoutWidget1)
        self.horizontalLayout1.setContentsMargins(10, 10,0, 10)

        self.label_ip_address = QLabel(self)
        self.label_ip_address.setText('IP地址:')
        self.horizontalLayout1.addWidget(self.label_ip_address)

        self.lineEdit_ip_address = QLineEdit(self)
        self.horizontalLayout1.addWidget(self.lineEdit_ip_address)

        self.horizontalLayoutWidget2 = QWidget(self)
        self.horizontalLayoutWidget2.setGeometry(QRect(170, 0, 100, 60))
        self.horizontalLayout2 = QHBoxLayout(self.horizontalLayoutWidget2)
        self.horizontalLayout2.setContentsMargins(5, 10, 10, 10)

        self.horizontalLayoutWidget3 = QWidget(self)
        self.horizontalLayoutWidget3.setGeometry(QRect(270, 0, 80, 60))
        self.horizontalLayout3 = QHBoxLayout(self.horizontalLayoutWidget3)
        self.horizontalLayout3.setContentsMargins(10, 10, 10, 10)

        self.btn_test = QPushButton(self)
        self.btn_test.setText('端口扫描')
        self.horizontalLayout3.addWidget(self.btn_test)

    def connect_all_signal_slot(self):
        self.btn_test.clicked.connect(self.btn_test_clicked)

    def btn_test_clicked(self):
        ip_address = self.lineEdit_ip_address.text()
        port = self.lineEdit_port.text()

        if ip_address == '':
            self.msg_failed('请填写IP地址')
            return

        if port == '':
            self.msg_failed('请填写端口')
            return

        # PI地址合法性匹配说明，^行首开始匹配，\d{1,3}匹配1-3个数字，(?:\.\d{1,3}){3} [.1-3个数字]匹配3次，(?!.)最后不能有任何字符
        pattern = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}(?!.)')
        s = pattern.findall(ip_address)
        if s == []:
            self.msg_failed("IP地址非法")
            return

        if pingIP(ip_address) == 1:
            logging.error('端口测试错误：IP地址无法PING通')
            self.msg_failed('IP地址无法PING通')
            return

        s = socket.socket()
        try:
            s.connect((ip_address, int(port)))
            self.msg_success('端口测试成功')
        except BaseException as e:
            logging.error('端口测试错误：{}'.format(e))
            self.msg_failed('端口测试错误：{}'.format(e))