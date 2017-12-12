# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import socket
import re

from InfoCoreTestPlatformBaseUI import BaseDlg1
from InfoCoreTools.WindowsCMD import pingIP
from ComputerPowerControlTool.ComputerPowerControlToolGlobalVals import machine_power_control_setting_dict
from ComputerPowerControlTool.ComputerPowerControlToolGlobalVals import machine_power_control_setting_file
from ComputerPowerControlTool.ComputerPowerControlToolClass import ComputerPowerControlMachine
from ComputerPowerControlTool.ComputerPowerControlToolFunctions import save_power_control_machine_setting_to_xls
from ComputerPowerControlTool.ComputerPowerControlToolThreads import PowerOnThread
from ComputerPowerControlTool.ComputerPowerControlToolThreads import PowerOffThread
from ComputerPowerControlTool.ComputerPowerControlToolThreads import RebootThread

logger = logging.getLogger('root.ComputerPowerControlTool.ComputerPowerControlToolUI')

class ComputerPowerControlToolDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(ComputerPowerControlToolDlg, self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('服务器电源控制')  # 设置窗口标题

        self.btn_add = QPushButton(self)
        self.btn_add.setText('添加')

        self.btn_delete = QPushButton(self)
        self.btn_delete.setText('删除')
        self.btn_delete.setDisabled(True)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')

        self.table = QTableWidget(self)  # 创建表
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止拖动列宽
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 按行选择模式
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择模式
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止修改单元格内容
        self.table.setAlternatingRowColors(True)  # 隔行变色
        self.table.setSortingEnabled(True)  # 表头排序self.table = QTableWidget(self)  # 创建表
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止拖动列宽
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 按行选择模式
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择模式
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止修改单元格内容
        self.table.setAlternatingRowColors(True)  # 隔行变色
        self.table.setSortingEnabled(True)  # 表头排序

        self.refresh_ui()

    def refresh_ui(self):
        self.table.setColumnCount(4)
        self.table.setRowCount(len(machine_power_control_setting_dict))

        logging.info('设置表头')
        horizontalHeader = ["设备类型", "操作系统类型", "IP地址", "操作"]
        self.table.setHorizontalHeaderLabels(horizontalHeader)
        logging.info('设置表内容')
        i = 0
        for ip in machine_power_control_setting_dict:
            server = machine_power_control_setting_dict[ip]
            try:
                self.table.setCellWidget(i, 0, self.buttonForShow(ip, server.computer_type))
                self.table.setItem(i, 1, QTableWidgetItem(server.os_type))
                self.table.setItem(i, 2, QTableWidgetItem(server.ip_address))
                self.table.setCellWidget(i, 3, self.buttonForControl(ip))
            except BaseException:
                logging.exception('未知错误')

            i = i + 1
        logging.info('表内容布置完毕')
        self.set_layout()

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.btn_delete.clicked.connect(self.btn_delete_clicked)
        self.table.clicked.connect(self.table_clicked)

    def table_clicked(self):
        self.btn_delete.setEnabled(True)

    def btn_delete_clicked(self):
        try:
            select_row = self.table.currentRow()
            select_ip = self.table.item(select_row,2).text()
            machine_power_control_setting_dict.pop(select_ip)
            self.refresh_ui()
        except BaseException:
            logging.exception('未知错误')

    def btn_save_clicked(self):
        if save_power_control_machine_setting_to_xls(machine_power_control_setting_file):
            self.msg_success('保存成功')
        else:
            self.msg_success('保存失败')

    def btn_add_clicked(self):
        add_machine_setting_dlg = AddMachineSettingDlg(self)
        add_machine_setting_dlg.sin1.connect(self.refresh_ui)
        add_machine_setting_dlg.show()

    def buttonForShow(self,ip,computer_type):
        horizontalLayoutWidget = QWidget()
        horizontalLayout = QHBoxLayout(horizontalLayoutWidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)

        show_detail = QPushButton()
        show_detail.setText(computer_type)
        horizontalLayout.addWidget(show_detail)
        show_detail.clicked.connect(lambda: self.show_detail_clicked(ip))
        return horizontalLayoutWidget

    def buttonForControl(self, ip):
        horizontalLayoutWidget = QWidget()
        horizontalLayout = QHBoxLayout(horizontalLayoutWidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)

        power_on = QPushButton('打开电源')
        horizontalLayout.addWidget(power_on)
        power_on.clicked.connect(lambda: self.power_on_clicked(ip))

        power_off = QPushButton('关闭电源')
        horizontalLayout.addWidget(power_off)
        power_off.clicked.connect(lambda:self.power_off_clicked(ip))

        shutdown = QPushButton('重启')
        horizontalLayout.addWidget(shutdown)
        shutdown.clicked.connect(lambda:self.shutdown_clicked(ip))
        return horizontalLayoutWidget

    def show_detail_clicked(self,ip):
        try:
            self.modify_machine_setting_dlg = ModifyMachineSettingDlg(ip)
            self.modify_machine_setting_dlg.sin1.connect(self.refresh_ui)
            self.modify_machine_setting_dlg.show()
        except BaseException:
            logging.exception('未知错误')

    def power_on_clicked(self,ip):
        server = machine_power_control_setting_dict[ip]
        logging.info("打开{}的电源".format(ip))
        self.power_on_thread = PowerOnThread(server)
        self.power_on_thread.start()

    def power_off_clicked(self,ip):
        server = machine_power_control_setting_dict[ip]
        logging.info("关闭{}的电源".format(ip))

        self.power_off_thread = PowerOffThread(server)
        self.power_off_thread.start()

    def shutdown_clicked(self,ip):
        server = machine_power_control_setting_dict[ip]
        logging.info("重启服务器{}".format(ip))
        self.reboot_thread = RebootThread(server)
        self.reboot_thread.start()

    def set_layout(self):
        try:
            logging.info("界面控件布局")
            x = 0
            y = 0
            self.btn_add.setGeometry(
                QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
                      self.y_up_margin_2,
                      self.button_width_50,
                      self.button_height_25))
            x = x + 1
            y = y + 1
            self.btn_delete.setGeometry(
                QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
                      self.y_up_margin_2,
                      self.button_width_50,
                      self.button_height_25))
            x = x + 1
            y = y + 1
            self.btn_save.setGeometry(
                QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
                      self.y_up_margin_2,
                      self.button_width_50,
                      self.button_height_25))

            self.table.resizeColumnsToContents()  # 设置自适应列宽
            self.table.resizeRowsToContents()  # 设置自适应行高
            col_width = 0  # 表格总宽
            for j in range(self.table.columnCount()):
                col_width = col_width + self.table.columnWidth(j)
            # col_width = col_width + 2  # 表格和表格桌布预留空间

            row_heigth = 0  # 表格总高(不含表头高度)
            for k in range(len(machine_power_control_setting_dict)):
                row_heigth = row_heigth + self.table.rowHeight(k)

            min_width = self.x_left_margin_2 * 2 + self.button_width_50 * 5 + self.button_width_80 + self.widget_width_space_5 * 4
            if col_width < min_width:
                col_width = min_width
                # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setGeometry(QRect(self.x_left_margin_2,  # 左边空余2个尺度
                                         self.y_up_margin_2 + self.button_height_25 + self.widget_heigth_space_5,
                                         # 上面空余2个尺度+一个按钮25尺度+5尺度控件间距
                                         col_width,
                                         row_heigth + self.table_head_heigth))
            self.resize(col_width + 2 * self.x_left_margin_2,
                        row_heigth + self.table_head_heigth + 2 * self.y_up_margin_2 + self.button_height_25 + self.widget_heigth_space_5)  # 设置窗口大小

            logging.info('界面控件布局结束')
        except BaseException:
            logging.exception('未知错误')

class AddMachineSettingDlg(BaseDlg1):
    sin1 = pyqtSignal() #自定义信号
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(AddMachineSettingDlg, self).__init__(parent)
        self.set_ui()

    def init_ui(self):
        self.resize(220, 400)
        self.setFixedSize(self.width(), self.height())
        self.setSizeGripEnabled(True)


        #添加栅格布局1
        self.gridLayoutWidget = QWidget(self)
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 200, 380))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        i = 0
        #设置界面上的各个标签布局
        self.label_computer_type = QLabel(self.gridLayoutWidget)
        self.label_computer_type.setText('设备类型：')
        self.gridLayout.addWidget(self.label_computer_type, i, 0)
        self.comboBox_computer_type = QComboBox(self.gridLayoutWidget)
        self.comboBox_computer_type.addItem("实体机")
        self.comboBox_computer_type.addItem("虚拟机")
        self.gridLayout.addWidget(self.comboBox_computer_type, i, 1)

        i = i + 1
        self.label_os_type = QLabel(self.gridLayoutWidget)
        self.label_os_type.setText('操作系统：')
        self.gridLayout.addWidget(self.label_os_type, i, 0)
        self.comboBox_os_type = QComboBox(self.gridLayoutWidget)
        self.comboBox_os_type.addItem("Windows")
        self.comboBox_os_type.addItem("Linux")
        self.gridLayout.addWidget(self.comboBox_os_type,i,1)

        i = i + 1
        self.label_ip_address = QLabel(self.gridLayoutWidget)
        self.label_ip_address.setText('IP地址：')
        self.gridLayout.addWidget(self.label_ip_address,i,0)
        self.qline_edit_ip_address = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_ip_address, i, 1)

        i = i + 1
        self.label_username = QLabel(self.gridLayoutWidget)
        self.label_username.setText('用户名：')
        self.gridLayout.addWidget(self.label_username, i, 0)
        self.qline_edit_username = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_username, i, 1)

        i = i + 1
        self.label_server_password = QLabel(self.gridLayoutWidget)
        self.label_server_password.setText('密码：')
        self.gridLayout.addWidget(self.label_server_password, i, 0)
        self.qline_edit_password = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_password, i, 1)

        # 添加复选框[是否配置IPMI]
        i = i + 1
        self.checkbox_is_enable_ipmi = QCheckBox(self.gridLayoutWidget)
        self.checkbox_is_enable_ipmi.setText("是否启用IPMI")
        self.gridLayout.addWidget(self.checkbox_is_enable_ipmi, i, 0)

        #IPMI信息
        i = i + 1
        self.label_ipmi_ip = QLabel(self.gridLayoutWidget)
        self.label_ipmi_ip.setText('IPMI IP：')
        self.gridLayout.addWidget(self.label_ipmi_ip, i, 0)
        self.qline_edit_ipmi_ip = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_ipmi_ip, i, 1)
        self.qline_edit_ipmi_ip.setDisabled(True)

        i = i + 1
        self.label_ipmi_username = QLabel(self.gridLayoutWidget)
        self.label_ipmi_username.setText("IPMI用户名：")
        self.gridLayout.addWidget(self.label_ipmi_username, i, 0)
        self.qline_edit_ipmi_username = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_ipmi_username, i, 1)
        self.qline_edit_ipmi_username.setDisabled(True)

        i = i + 1
        self.label_ipmi_password = QLabel(self.gridLayoutWidget)
        self.label_ipmi_password.setText('IPMI密码：')
        self.gridLayout.addWidget(self.label_ipmi_password, i, 0)
        self.qline_edit_ipmi_password = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_ipmi_password, i, 1)
        self.qline_edit_ipmi_password.setDisabled(True)

        #添加复选框[是否虚拟机]
        i = i + 1
        self.checkbox_is_virtual_machine = QCheckBox(self.gridLayoutWidget)
        self.checkbox_is_virtual_machine.setText("是否为虚拟机")
        self.gridLayout.addWidget(self.checkbox_is_virtual_machine, i, 0)

        # 设置栅格布局3的各个标签布局
        i = i + 1
        self.label_virtual_machine_name = QLabel(self.gridLayoutWidget)
        self.label_virtual_machine_name.setText('虚拟机名：')
        self.gridLayout.addWidget(self.label_virtual_machine_name, i, 0)
        self.qline_edit_virtual_machine_name = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_virtual_machine_name, i, 1)
        self.qline_edit_virtual_machine_name.setDisabled(True)

        i = i + 1
        self.label_host_ip = QLabel(self.gridLayoutWidget)
        self.label_host_ip.setText("主机IP地址：")
        self.gridLayout.addWidget(self.label_host_ip, i, 0)
        self.qline_edit_esxi_ip = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_esxi_ip, i, 1)
        self.qline_edit_esxi_ip.setDisabled(True)

        i = i + 1
        self.label_host_username = QLabel(self.gridLayoutWidget)
        self.label_host_username.setText('主机用户名：')
        self.gridLayout.addWidget(self.label_host_username, i, 0)
        self.qline_edit_esxi_username = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_esxi_username, i, 1)
        self.qline_edit_esxi_username.setDisabled(True)

        i = i + 1
        self.label_host_password = QLabel(self.gridLayoutWidget)
        self.label_host_password.setText('主机密码：')
        self.gridLayout.addWidget(self.label_host_password, i, 0)
        self.qline_edit_esxi_password = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.qline_edit_esxi_password, i, 1)
        self.qline_edit_esxi_password.setDisabled(True)

        # 添加应用按钮
        i = i + 1
        self.btn_apply = QPushButton(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.btn_apply, i, 1)
        self.btn_apply.setDisabled(True)

        #设置信号槽
        self.btn_apply.clicked.connect(self.clicked_btn_apply)
        self.qline_edit_ip_address.textChanged.connect(self.widget_changed)
        self.qline_edit_username.textChanged.connect(self.widget_changed)
        self.qline_edit_password.textChanged.connect(self.widget_changed)
        self.qline_edit_ipmi_ip.textChanged.connect(self.widget_changed)
        self.qline_edit_ipmi_username.textChanged.connect(self.widget_changed)
        self.qline_edit_ipmi_password.textChanged.connect(self.widget_changed)
        self.qline_edit_virtual_machine_name.textChanged.connect(self.widget_changed)
        self.qline_edit_esxi_ip.textChanged.connect(self.widget_changed)
        self.qline_edit_esxi_username.textChanged.connect(self.widget_changed)
        self.qline_edit_esxi_password.textChanged.connect(self.widget_changed)
        self.checkbox_is_virtual_machine.stateChanged.connect(self.widget_changed)
        self.checkbox_is_enable_ipmi.stateChanged.connect(self.widget_changed)

    def set_ui(self):
        self.setWindowTitle("添加服务器")
        self.btn_apply.setText("添加")

    def widget_changed(self):
        ip_address = self.qline_edit_ip_address.text()
        username = self.qline_edit_username.text()
        password = self.qline_edit_password.text()

        flag = True
        if ip_address == '':
            flag = False
        if username == '':
            flag = False
        if password == '':
            flag = False

        if self.checkbox_is_enable_ipmi.isChecked():
            self.qline_edit_ipmi_ip.setEnabled(True)
            self.qline_edit_ipmi_username.setEnabled(True)
            self.qline_edit_ipmi_password.setEnabled(True)

            ipmi_ip = self.qline_edit_ipmi_ip.text()
            ipmi_username = self.qline_edit_ipmi_username.text()
            ipmi_password = self.qline_edit_ipmi_password.text()
            if ipmi_ip == '':
                flag = False
            if ipmi_username == '':
                flag = False
            if ipmi_password == '':
                flag = False

        else:
            self.qline_edit_ipmi_ip.setDisabled(True)
            self.qline_edit_ipmi_username.setDisabled(True)
            self.qline_edit_ipmi_password.setDisabled(True)

        if self.checkbox_is_virtual_machine.isChecked():
            self.qline_edit_virtual_machine_name.setEnabled(True)
            self.qline_edit_esxi_username.setEnabled(True)
            self.qline_edit_esxi_ip.setEnabled(True)
            self.qline_edit_esxi_password.setEnabled(True)

            vm_name = self.qline_edit_virtual_machine_name.text()
            host_ip = self.qline_edit_esxi_ip.text()
            host_username = self.qline_edit_username.text()
            host_password = self.qline_edit_password.text()
            if vm_name == '':
                flag = False
            if host_ip == '':
                flag = False
            if host_username == '':
                flag = False
            if host_password == '':
                flag = False

        else:
            self.qline_edit_virtual_machine_name.setDisabled(True)
            self.qline_edit_esxi_username.setDisabled(True)
            self.qline_edit_esxi_ip.setDisabled(True)
            self.qline_edit_esxi_password.setDisabled(True)

        if flag:
            self.btn_apply.setDisabled(False)
        else:
            self.btn_apply.setDisabled(True)

    def clicked_btn_apply(self):
        server = ComputerPowerControlMachine()
        server.computer_type = self.comboBox_computer_type.currentText()
        server.os_type = self.comboBox_os_type.currentText()
        server.ip_address = self.qline_edit_ip_address.text()
        server.username = self.qline_edit_username.text()
        server.password = self.qline_edit_password.text()
        server.is_ipmi_enabled = False
        server.ipmi_ip = ''
        server.ipmi_username = ''
        server.ipmi_password = ''
        server.is_vm = False
        server.vm_name = ''
        server.esxi_ip = ''
        server.esxi_username = ''
        server.esxi_password = ''

        if self.checkbox_is_enable_ipmi.isChecked():
            server.is_ipmi_enabled = True
            server.ipmi_ip = self.qline_edit_ipmi_ip.text()
            server.ipmi_username = self.qline_edit_ipmi_username.text()
            server.ipmi_password = self.qline_edit_ipmi_password.text()

        if self.checkbox_is_virtual_machine.isChecked():
            server.is_vm = True
            server.vm_name = self.qline_edit_virtual_machine_name.text()
            server.esxi_ip = self.qline_edit_esxi_ip.text()
            server.esxi_username = self.qline_edit_esxi_username.text()
            server.esxi_password = self.qline_edit_esxi_password.text()
        machine_power_control_setting_dict[server.ip_address] = server

        self.sin1.emit()  # 发射自定义信号（配置更新后发射信号）
        self.close()

class ModifyMachineSettingDlg(AddMachineSettingDlg):
    sin1 = pyqtSignal()  # 自定义信号
    def __init__(self, ip, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(ModifyMachineSettingDlg, self).__init__(parent)
        self.ip = ip
        self.set_default(self.ip)

    def set_ui(self):
        self.setWindowTitle("修改服务器")
        self.btn_apply.setText("确定")
        self.qline_edit_ip_address.setDisabled(True)

    def set_default(self,ip_address):
        try:
            server = machine_power_control_setting_dict[ip_address]
            if server.computer_type == '实体机':
                self.comboBox_computer_type.setCurrentText('实体机')
            else:
                self.comboBox_computer_type.setCurrentText('虚拟机')
            if server.os_type == 'Windows':
                self.comboBox_os_type.setCurrentText('Windows')
            else:
                self.comboBox_os_type.setCurrentText('Linux')
            self.qline_edit_ip_address.setText(server.ip_address)
            self.qline_edit_username.setText(server.username)
            self.qline_edit_password.setText(server.password)
            if server.is_ipmi_enabled:
                self.checkbox_is_enable_ipmi.setChecked(True)
                self.qline_edit_ipmi_ip.setText(server.ipmi_ip)
                self.qline_edit_ipmi_username.setText(server.ipmi_username)
                self.qline_edit_ipmi_password.setText(server.ipmi_password)
            if server.is_vm:
                self.checkbox_is_virtual_machine.setChecked(True)
                self.qline_edit_esxi_ip.setText(server.esxi_ip)
                self.qline_edit_esxi_username.setText(server.esxi_username)
                self.qline_edit_esxi_password.setText(server.esxi_password)
                self.qline_edit_virtual_machine_name.setText(server.vm_name)
        except BaseException:
            logging.exception('未知错误')

