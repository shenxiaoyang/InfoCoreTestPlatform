# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import os

from StreamerTestPlatformGlobalVars import run_path,total_roles,total_os_types
from StreamerTestPlatformBaseUI import BaseDlg1
from LogCollectTool.LogCollectToolClass import LogCollectToolMachine
from LogCollectTool.LogCollectToolGlobalVars import machine_setting_dict
from LogCollectTool.LogCollectToolGlobalVars import log_path_setting_dict
from LogCollectTool.LogCollectToolGlobalVars import parameters_setting_dict
from LogCollectTool.LogCollectToolGlobalVars import LOG_COLLECT_TOOL_UI_UPDATE_EVENT
from LogCollectTool.LogCollectToolGlobalVars import machine_setting_file
from LogCollectTool.LogCollectToolGlobalVars import log_path_setting_file
from LogCollectTool.LogCollectToolThreads import CopyWindowsFileThread
from LogCollectTool.LogCollectToolThreads import CopyLinuxFileThread
from LogCollectTool.LogCollectToolThreads import CopyLocalStreamerConsoleFileThread
from LogCollectTool.LogCollectToolThreads import ThreadNumCheckThread
from LogCollectTool.LogCollectToolFunctions import save_machine_setting_to_xls
from LogCollectTool.LogCollectToolFunctions import save_log_path_setting_to_xls
from InfoCoreTools import WindowsCMD
from InfoCoreTools import Time

logger = logging.getLogger('root.LogCollectToolUI')

#监控线程，主要用于监控界面是否有更新，如果有更新，则刷新相应的界面
class MonitorUIThread(QThread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    signal_update_btn_collect_log = pyqtSignal()  # 自定义信号

    def __init__(self, event ,parent=None):
        super(MonitorUIThread, self).__init__(parent)
        self.event = event

    def run(self):
        while 1:
            self.event.wait()   #阻塞线程，等待外部事件响应
            self.signal_update_btn_collect_log.emit() #发射信号
            self.event.clear()  #重新设置线程阻塞

#对话框-日志收集工具
class LogCollectToolDlg(BaseDlg1):
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(LogCollectToolDlg,self).__init__(parent)
        self.start_monitor_ui_thread()
        self.default_set()

    def init_ui(self):
        server_num = len(machine_setting_dict)
        self.setObjectName("MainWindow")
        self.resize(300, 20+20*server_num+60)  # 设置窗口大小
        #self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.setWindowTitle('日志收集工具')

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(20, 20, 260, server_num*20))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.checkBox_server = {}
        for ip_address in machine_setting_dict:
            self.checkBox_server[ip_address] = QCheckBox(self.verticalLayoutWidget)
            self.verticalLayout.addWidget(self.checkBox_server[ip_address])
            self.checkBox_server[ip_address].setText("{}[{}]".format(ip_address,machine_setting_dict[ip_address].role))

        self.btn_collect_log = QPushButton(self)
        self.btn_collect_log.setGeometry(QRect(200, 40 + server_num * 20, 80, 25))
        self.btn_collect_log.setText('收集日志')
        self.btn_collect_log.setDisabled(True)

        self.btn_edit_machine_setting = QPushButton(self)
        self.btn_edit_machine_setting.setGeometry(QRect(20, 40 + server_num * 20, 80, 25))
        self.btn_edit_machine_setting.setText('修改服务器')

        self.btn_edit_log_path_setting = QPushButton(self)
        self.btn_edit_log_path_setting.setGeometry(QRect(110, 40 + server_num * 20, 80, 25))
        self.btn_edit_log_path_setting.setText('修改收集内容')

    def connect_all_signal_slot(self):
        self.btn_collect_log.clicked.connect(self.btn_collect_log_clicked)
        for ip_address in self.checkBox_server:
            self.checkBox_server[ip_address].clicked.connect(self.checkBok_server_clicked)
        self.btn_edit_machine_setting.clicked.connect(self.btn_edit_machine_setting_clicked)
        self.btn_edit_log_path_setting.clicked.connect(self.btn_edit_log_path_setting_clicked)

    def btn_edit_log_path_setting_clicked(self):
        edit_log_path_setting_dlg = EditLogPathSetting(self)
        logging.info('打开修改收集内容对话框')
        edit_log_path_setting_dlg.show()

    def btn_edit_machine_setting_clicked(self):
        edit_machine_setting_dlg = EditMachineSetting(self)
        logging.info('打开修改服务器对话框')
        edit_machine_setting_dlg.show()
        edit_machine_setting_dlg.sin2.connect(self.update_ui)

    def update_ui(self):
        server_num = len(machine_setting_dict)
        self.resize(300, 20 + 20 * server_num + 60)  # 设置窗口大小
        self.verticalLayoutWidget.setGeometry(QRect(20, 20, 260, server_num * 20))
        for ip_addr in self.checkBox_server:    #删除了IP情况
            try:
                tmp = machine_setting_dict[ip_addr]
            except KeyError:
                self.checkBox_server[ip_addr].close()
                self.verticalLayout.removeWidget(self.checkBox_server[ip_addr])

        for ip_address in machine_setting_dict: #添加了IP情况
            try:
                tmp = self.checkBox_server[ip_address]
            except KeyError:
                self.checkBox_server[ip_address] = QCheckBox(self.verticalLayoutWidget)
                self.verticalLayout.addWidget(self.checkBox_server[ip_address])
                self.checkBox_server[ip_address].setText("{}[{}]".format(ip_address, machine_setting_dict[ip_address].role))
                self.checkBox_server[ip_address].clicked.connect(self.checkBok_server_clicked)

        self.btn_collect_log.setGeometry(QRect(200, 40 + server_num * 20, 80, 25))
        self.btn_edit_machine_setting.setGeometry(QRect(20, 40 + server_num * 20, 80, 25))
        self.btn_edit_log_path_setting.setGeometry(QRect(110, 40 + server_num * 20, 80, 25))

    def default_set(self):
        pass

    def checkBok_server_clicked(self):
        flag = False
        logging.debug('====================')
        for ip_address in self.checkBox_server:
            if self.checkBox_server[ip_address].isChecked():
                logging.debug('选中{}'.format(ip_address))
                flag = True
                #break
            else:
                logging.debug('取消选中{}'.format(ip_address))
        logging.debug('====================')

        if flag:
            self.btn_collect_log.setEnabled(True)
        else:
            self.btn_collect_log.setDisabled(True)

    def start_monitor_ui_thread(self):
        logging.info('启动日志收集工具主页面后台刷新监控线程')
        self.monitor_ui_thread = MonitorUIThread(LOG_COLLECT_TOOL_UI_UPDATE_EVENT)    #注册事件器
        self.monitor_ui_thread.start()  #启动线程
        self.monitor_ui_thread.signal_update_btn_collect_log.connect(self.update_btn_collect_log_status)   #设置信号槽[用于更新树列表]

    def btn_collect_log_clicked(self):
        self.btn_collect_log.setDisabled(True)  #禁用收集按钮，防止连续二次收集
        self.btn_collect_log.setText('日志收集中')
        logging.info('生成时间字符串')
        date_string = Time.getCurrentDatetimeString(parameters_setting_dict['suffix'])  # 获取时间字符串
        try:
            for ip_address in self.checkBox_server: #遍历所有的复选框
                if self.checkBox_server[ip_address].isChecked() == True:    #如果复选框被选中
                    if WindowsCMD.pingIP(ip_address) == 0:  #如果此IP地址在线
                        server = machine_setting_dict[ip_address]
                        role = machine_setting_dict[ip_address].role
                        if role == 'StreamerWindowsClient': #如果选中IP地址为StreamerWindows客户端
                            ip_string = ip_address.replace('.', '_')
                            local_path = '{}\{}\Streamer_WClient\{}'.format(run_path, date_string, ip_string)
                            if not os.path.exists(local_path):
                                os.makedirs(local_path)  # 创建文件夹
                            # 创建一个线程，收集StreamerWindowsClient的日志
                            collect_streamer_wclient_log_thread = CopyWindowsFileThread(server.ip_address,
                                                                                        server.username,
                                                                                        server.password,
                                                                                        log_path_setting_dict[role],
                                                                                        local_path)
                            logging.info('准备收集Windows客户端：{}的日志'.format(ip_address))
                            # 开始Windows客户端日志收集线程
                            collect_streamer_wclient_log_thread.start()
                        elif role == 'StreamerLinuxClient':  # 如果是Linux客户端
                            ip_string = ip_address.replace('.', '_')
                            local_path = '{}\{}\Streamer_LClient\{}'.format(run_path, date_string, ip_string)
                            if not os.path.exists(local_path):
                                os.makedirs(local_path)  # 创建文件夹
                            # 创建一个线程，收集StreamerLinuxClient的日志
                            collect_streamer_lclient_log_thread = CopyLinuxFileThread(server.ip_address,
                                                                                      server.username,
                                                                                      server.password,
                                                                                      log_path_setting_dict[role],
                                                                                      local_path)
                            logging.info('准备收集Linux客户端：{}的日志'.format(ip_address))
                            # 开始Linux客户端日志收集线程
                            collect_streamer_lclient_log_thread.start()
                        elif role == 'StreamerServer':  # 如果是Stremer Server
                            ip_string = ip_address.replace('.', '_')
                            local_path = '{}\{}\Streamer_Server\{}'.format(run_path, date_string, ip_string)  # 本地存放日志文件夹
                            if not os.path.exists(local_path):
                                os.makedirs(local_path)  # 创建文件夹

                            # 创建一个线程，收集StreamerServer的日志
                            collect_streamer_server_log_thread = CopyLinuxFileThread(server.ip_address,
                                                                                     server.username,
                                                                                     server.password,
                                                                                     log_path_setting_dict[role],
                                                                                     local_path)
                            logging.info('准备收集Streamer服务端：{}的日志'.format(ip_address))
                            # 开始Streamer服务端日志收集线程
                            collect_streamer_server_log_thread.start()
                        elif role == 'LocalStreamerConsole':    #如果选中的是本地的控制台
                            ip_string = ip_address.replace('.', '_')
                            local_path = '{}\{}\Streamer_Console\{}'.format(run_path, date_string, ip_string)  # 本地存放日志文件夹
                            if not os.path.exists(local_path):
                                os.makedirs(local_path)  # 创建文件夹
                            collect_local_streamer_console_thread = CopyLocalStreamerConsoleFileThread(log_path_setting_dict[role], local_path)
                            logging.info('准备收集本机Streamer控制台：{}的日志'.format(ip_address))
                            collect_local_streamer_console_thread.start()
                        elif role == 'VMware':
                            logging.info('暂时不支持VMware日志收集')
                        elif role == 'Oracle':
                            logging.info('暂时不支持Oracle日志收集')
                        else:
                            logging.warning('未知类型的角色{}'.format(machine_setting_dict[ip_address].role))
                    else:
                        logging.info('IP：{}不在线，无法收集日志'.format(ip_address))
        except BaseException:
            logging.exception('未知错误')
        logging.info('启动日志收集统计监控线程')
        self.thread_num_check = ThreadNumCheckThread()
        self.thread_num_check.start()

    def update_btn_collect_log_status(self):
        self.btn_collect_log.setEnabled(True)
        self.btn_collect_log.setText('收集日志')
        self.msg_success('日志收集完毕')

    def closeEvent(self, QCloseEvent):
        machine_setting_dict.clear()
        log_path_setting_dict.clear()

#对话框-修改服务器
class EditMachineSetting(BaseDlg1):
    sin2 = pyqtSignal()  # 自定义信号
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(EditMachineSetting,self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('修改服务器')    #设置窗口标题

        self.btn_add = QPushButton(self)
        self.btn_add.setText('添加')
        self.btn_add.setGeometry(QRect(self.x_left_margin_2, self.y_up_margin_2, self.button_width_60, self.button_height_25))

        self.btn_delete = QPushButton(self)
        self.btn_delete.setText('删除')
        self.btn_delete.setGeometry(QRect(self.x_left_margin_2 + self.button_width_60, self.y_up_margin_2, self.button_width_60, self.button_height_25))
        self.btn_delete.setDisabled(True)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(QRect(self.x_left_margin_2 + self.button_width_60 * 2, self.y_up_margin_2, self.button_width_60, self.button_height_25))

        self.table = QTableWidget(self) #创建表
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止拖动列宽
        self.table.setSelectionBehavior(QTableWidget.SelectRows)    #按行选择模式
        self.table.setSelectionMode(QTableWidget.SingleSelection)   #单行选择模式
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) #禁止修改单元格内容
        self.table.setAlternatingRowColors(True)    #隔行变色
        self.table.setColumnCount(5)
        self.table.setRowCount(len(machine_setting_dict))

        horizontalHeader = ["角色", "操作系统", "IP", "用户名", "密码"]
        self.table.setHorizontalHeaderLabels(horizontalHeader)
        i=0
        for ip in machine_setting_dict:
            server = machine_setting_dict[ip]
            self.table.setItem(i, 0, QTableWidgetItem(server.role))
            self.table.setItem(i, 1, QTableWidgetItem(server.os_type))
            self.table.setItem(i, 2, QTableWidgetItem(server.ip_address))
            self.table.setItem(i, 3, QTableWidgetItem(server.username))
            self.table.setItem(i, 4, QTableWidgetItem(server.password))
            i=i+1
        self.table.resizeColumnsToContents()    #设置自适应列宽
        self.table.resizeRowsToContents()   #设置自适应行高

        col_width = 0 #表格总宽
        for j in range(self.table.columnCount()):
            col_width = col_width + self.table.columnWidth(j)
        col_width=col_width+2   #表格和表格桌布预留空间

        row_heigth = 0  #表格总高(不含表头高度)
        for k in range(i):
            row_heigth = row_heigth + self.table.rowHeight(k)
        header_heigth = 28

        self.table.setGeometry(QRect(self.x_left_margin_2,
                                     self.y_up_margin_2 + self.button_height_25,
                                     col_width,
                                     row_heigth + header_heigth)) #根据表格总宽度和总高设置表格大小
        self.resize(col_width + 2 * self.x_left_margin_2,
                    row_heigth + header_heigth + 2 * self.y_up_margin_2 + self.button_height_25)  # 设置窗口大小

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn_delete.clicked.connect(self.btn_delete_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)

    def btn_save_clicked(self):
        if save_machine_setting_to_xls(machine_setting_file):
            self.msg_success('保存成功')
        else:
            self.msg_success('保存失败')

    def table_clicked(self):
        self.btn_delete.setEnabled(True)

    def btn_delete_clicked(self):
        select_row = self.table.currentRow()
        select_ip = self.table.item(select_row,2).text()
        machine_setting_dict.pop(select_ip)
        self.update_ui()

    def btn_add_clicked(self):
        add_machine_dlg = AddMachineSetting(self)
        add_machine_dlg.sin1.connect(self.update_ui)
        add_machine_dlg.show()

    def update_ui(self):
        self.table.setColumnCount(5)
        self.table.setRowCount(len(machine_setting_dict))
        horizontalHeader = ["角色", "操作系统", "IP", "用户名", "密码"]
        self.table.setHorizontalHeaderLabels(horizontalHeader)
        i = 0
        for ip in machine_setting_dict:
            server = machine_setting_dict[ip]
            self.table.setItem(i, 0, QTableWidgetItem(server.role))
            self.table.setItem(i, 1, QTableWidgetItem(server.os_type))
            self.table.setItem(i, 2, QTableWidgetItem(server.ip_address))
            self.table.setItem(i, 3, QTableWidgetItem(server.username))
            self.table.setItem(i, 4, QTableWidgetItem(server.password))
            i = i + 1

        self.table.resizeColumnsToContents()  # 设置自适应列宽
        self.table.resizeRowsToContents()  # 设置自适应行高

        col_width = 0  # 表格总宽
        for j in range(self.table.columnCount()):
            col_width = col_width + self.table.columnWidth(j)
        col_width = col_width + 2  # 表格和表格桌布预留空间

        row_heigth = 0  # 表格总高(不含表头高度)
        for k in range(i):
            row_heigth = row_heigth + self.table.rowHeight(k)
        header_heigth = 28

        self.table.setGeometry(QRect(self.x_left_margin_2,
                                     self.y_up_margin_2 + self.button_height_25,
                                     col_width,
                                     row_heigth + header_heigth))  # 根据表格总宽度和总高设置表格大小
        self.resize(col_width + 2 * self.x_left_margin_2,
                    row_heigth + header_heigth + 2 * self.y_up_margin_2 + self.button_height_25)  # 设置窗口大小

    def closeEvent(self, QCloseEvent):
        self.sin2.emit()

#对话框-添加服务器
class AddMachineSetting(BaseDlg1):
    sin1 = pyqtSignal()  # 自定义信号
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(AddMachineSetting,self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('添加服务器')  # 设置窗口标题
        self.resize(200,
                    self.y_up_margin_10 + self.button_height_25 * 5 + self.y_up_margin_10 + self.button_height_25 + self.y_up_margin_10)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        grid_layout_widget_width = 180
        grid_layout_widget_heigth = self.button_height_25 * 5

        #添加栅格布局1
        self.gridLayoutWidget_1 = QWidget(self)
        self.gridLayoutWidget_1.setGeometry(QRect(self.x_left_margin_10,
                                                  self.y_up_margin_10,
                                                  grid_layout_widget_width,
                                                  grid_layout_widget_heigth))
        self.gridLayoutWidget_1.setObjectName("gridLayoutWidget_1")
        self.gridLayout = QGridLayout(self.gridLayoutWidget_1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        #设置界面上的各个标签布局
        self.label_role = QLabel(self.gridLayoutWidget_1)
        self.label_role.setObjectName("label_role")
        self.gridLayout.addWidget(self.label_role, 1, 1)
        self.label_role.setText('角色')

        self.label_os_type = QLabel(self.gridLayoutWidget_1)
        self.label_os_type.setObjectName("label_os_type")
        self.gridLayout.addWidget(self.label_os_type, 2, 1)
        self.label_os_type.setText('操作系统')

        self.label_ip_address = QLabel(self.gridLayoutWidget_1)
        self.label_ip_address.setObjectName("label_ip_address")
        self.gridLayout.addWidget(self.label_ip_address, 3, 1)
        self.label_ip_address.setText('IP地址')

        self.label_username = QLabel(self.gridLayoutWidget_1)
        self.label_username.setObjectName("label_username")
        self.gridLayout.addWidget(self.label_username, 4, 1)
        self.label_username.setText('用户名')

        self.label_password = QLabel(self.gridLayoutWidget_1)
        self.label_password.setObjectName("label_password")
        self.gridLayout.addWidget(self.label_password, 5, 1)
        self.label_password.setText('密码')

        # 界面上个各个文本编辑框布局
        self.qline_edit_role = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_role.setObjectName("qline_edit_role")
        self.gridLayout.addWidget(self.qline_edit_role, 1, 2, 1, 1)

        self.qline_edit_os_type = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_os_type.setObjectName("qline_edit_os_type")
        self.gridLayout.addWidget(self.qline_edit_os_type, 2, 2, 1, 1)

        self.qline_edit_ip_address = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_ip_address.setObjectName("qline_edit_ip_address")
        self.gridLayout.addWidget(self.qline_edit_ip_address, 3, 2, 1, 1)

        self.qline_edit_username = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_username.setObjectName("qline_edit_username")
        self.gridLayout.addWidget(self.qline_edit_username, 4, 2, 1, 1)

        self.qline_edit_password = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_password.setObjectName("qline_edit_password")
        self.gridLayout.addWidget(self.qline_edit_password, 5, 2, 1, 1)

        self.btn_add = QPushButton(self)
        self.btn_add.setText("添加")
        self.btn_add.setGeometry(QRect(self.x_left_margin_10 + grid_layout_widget_width - self.button_width_60,
                                       self.y_up_margin_10 + grid_layout_widget_heigth + self.y_up_margin_10,
                                       self.button_width_60,
                                       self.button_height_25))

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)

    def btn_add_clicked(self):
        role = self.qline_edit_role.text()
        os_type = self.qline_edit_os_type.text()
        ip_address = self.qline_edit_ip_address.text()
        username = self.qline_edit_username.text()
        password = self.qline_edit_password.text()

        try:
            role = total_roles[role]
        except KeyError:
            self.msg_failed('角色不对,应为以下的其中一种\n{}'.format(total_roles.keys()))
            return

        try:
            os_type = total_os_types[os_type]
        except KeyError:
            self.msg_failed('操作系统不对,应为以下的其中一种\n{}'.format(total_os_types.keys()))
            return

        if ip_address == '':
            self.msg_failed('请填写IP地址')
            return

        if username == '':
            self.msg_failed('请填写用户名')
            return

        if password == '':
            self.msg_failed('请填写密码')
            return

        new_server = LogCollectToolMachine()
        new_server.role = role
        new_server.os_type = os_type
        new_server.ip_address = ip_address
        new_server.username = username
        new_server.password = password
        machine_setting_dict[ip_address] = new_server

        self.sin1.emit()
        self.close()

#对话框-修改收集内容
class EditLogPathSetting(BaseDlg1):
    sin2 = pyqtSignal()  # 自定义信号
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(EditLogPathSetting,self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('修改收集内容')  # 设置窗口标题

        self.btn_add = QPushButton(self)
        self.btn_add.setText('添加')
        self.btn_add.setGeometry(QRect(self.x_left_margin_2, self.y_up_margin_2, self.button_width_60, self.button_height_25))

        self.btn_delete = QPushButton(self)
        self.btn_delete.setText('删除')
        self.btn_delete.setGeometry(
            QRect(self.x_left_margin_2 + self.button_width_60, self.y_up_margin_2, self.button_width_60, self.button_height_25))
        self.btn_delete.setDisabled(True)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(
            QRect(self.x_left_margin_2 + self.button_width_60 * 2, self.y_up_margin_2, self.button_width_60, self.button_height_25))

        self.table = QTableWidget(self)  # 创建表
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止拖动列宽
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 按行选择模式
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择模式
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止修改单元格内容
        self.table.setAlternatingRowColors(True)  # 隔行变色
        self.table.setColumnCount(3)
        row_count = 0
        for role in log_path_setting_dict:
            for path in log_path_setting_dict[role]:
                row_count = row_count + 1
        self.table.setRowCount(row_count)

        horizontalHeader = ["类型", "路径", "是否文件夹"]
        self.table.setHorizontalHeaderLabels(horizontalHeader)
        i = 0
        for role in log_path_setting_dict:
            for path in log_path_setting_dict[role]:
                is_dirs = log_path_setting_dict[role][path]
                self.table.setItem(i, 0, QTableWidgetItem(role))
                self.table.setItem(i, 1, QTableWidgetItem(path))
                self.table.setItem(i, 2, QTableWidgetItem(is_dirs))
                i = i + 1
        self.table.resizeColumnsToContents()  # 设置自适应列宽
        self.table.resizeRowsToContents()  # 设置自适应行高

        col_width = 0  # 表格总宽
        for j in range(self.table.columnCount()):
            col_width = col_width + self.table.columnWidth(j)
        col_width = col_width + 2  # 表格和表格桌布预留空间

        row_heigth = 0  # 表格总高(不含表头高度)
        for k in range(i):
            row_heigth = row_heigth + self.table.rowHeight(k)
        header_heigth = 28

        self.table.setGeometry(QRect(self.x_left_margin_2,
                                     self.y_up_margin_2 + self.button_height_25,
                                     col_width,
                                     row_heigth + header_heigth))  # 根据表格总宽度和总高设置表格大小
        self.resize(col_width + 2 * self.x_left_margin_2,
                    row_heigth + header_heigth + 2 * self.y_up_margin_2 + self.button_height_25)  # 设置窗口大小

    def btn_save_clicked(self):
        if save_log_path_setting_to_xls(log_path_setting_file):
            self.msg_success('保存成功')
        else:
            self.msg_success('保存失败')

    def table_clicked(self):
        self.btn_delete.setEnabled(True)

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn_delete.clicked.connect(self.btn_delete_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)

    def btn_delete_clicked(self):
        select_row = self.table.currentRow()
        select_role = self.table.item(select_row, 0).text()
        select_path = self.table.item(select_row, 1).text()
        if len(log_path_setting_dict[select_role]) == 1:
            log_path_setting_dict.pop(select_role)
        else:
            log_path_setting_dict[select_role].pop(select_path)
        self.update_ui()

    def btn_add_clicked(self):
        log_path_setting_dlg = AddLogPathSetting(self)
        log_path_setting_dlg.sin1.connect(self.update_ui)
        log_path_setting_dlg.show()

    def update_ui(self):
        self.table.setColumnCount(3)
        row_count = 0
        for role in log_path_setting_dict:
            for path in log_path_setting_dict[role]:
                row_count = row_count + 1
        self.table.setRowCount(row_count)

        horizontalHeader = ["类型", "路径", "是否文件夹"]
        self.table.setHorizontalHeaderLabels(horizontalHeader)
        i = 0
        for role in log_path_setting_dict:
            for path in log_path_setting_dict[role]:
                is_dirs = log_path_setting_dict[role][path]
                self.table.setItem(i, 0, QTableWidgetItem(role))
                self.table.setItem(i, 1, QTableWidgetItem(path))
                self.table.setItem(i, 2, QTableWidgetItem(is_dirs))
                i = i + 1
        self.table.resizeColumnsToContents()  # 设置自适应列宽
        self.table.resizeRowsToContents()  # 设置自适应行高

        col_width = 0  # 表格总宽
        for j in range(self.table.columnCount()):
            col_width = col_width + self.table.columnWidth(j)
        col_width = col_width + 2  # 表格和表格桌布预留空间

        row_heigth = 0  # 表格总高(不含表头高度)
        for k in range(i):
            row_heigth = row_heigth + self.table.rowHeight(k)
        header_heigth = 28

        self.table.setGeometry(QRect(self.x_left_margin_2,
                                     self.y_up_margin_2 + self.button_height_25,
                                     col_width,
                                     row_heigth + header_heigth))  # 根据表格总宽度和总高设置表格大小
        self.resize(col_width + 2 * self.x_left_margin_2,
                    row_heigth + header_heigth + 2 * self.y_up_margin_2 + self.button_height_25)  # 设置窗口大小

#对话框-添加路径
class AddLogPathSetting(BaseDlg1):
    sin1 = pyqtSignal()  # 自定义信号
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(AddLogPathSetting,self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('添加路径')  # 设置窗口标题
        self.resize(200,
                    self.y_up_margin_10 + self.button_height_25 * 3 + self.y_up_margin_10 + self.button_height_25 + self.y_up_margin_10)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        grid_layout_widget_width = 180
        grid_layout_widget_heigth = self.button_height_25 * 3

        # 添加栅格布局1
        self.gridLayoutWidget_1 = QWidget(self)
        self.gridLayoutWidget_1.setGeometry(QRect(self.x_left_margin_10,
                                                  self.y_up_margin_10,
                                                  grid_layout_widget_width,
                                                  grid_layout_widget_heigth))
        self.gridLayoutWidget_1.setObjectName("gridLayoutWidget_1")
        self.gridLayout = QGridLayout(self.gridLayoutWidget_1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        # 设置界面上的各个标签布局
        self.label_role = QLabel(self.gridLayoutWidget_1)
        self.label_role.setObjectName("label_role")
        self.gridLayout.addWidget(self.label_role, 1, 1)
        self.label_role.setText('角色')

        self.label_log_path = QLabel(self.gridLayoutWidget_1)
        self.label_log_path.setObjectName("label_log_path")
        self.gridLayout.addWidget(self.label_log_path, 2, 1)
        self.label_log_path.setText('路径')

        self.label_is_dirs = QLabel(self.gridLayoutWidget_1)
        self.label_is_dirs.setObjectName("label_ip_address")
        self.gridLayout.addWidget(self.label_is_dirs, 3, 1)
        self.label_is_dirs.setText('是否文件夹')

        # 界面上个各个文本编辑框布局
        self.qline_edit_role = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_role.setObjectName("qline_edit_role")
        self.gridLayout.addWidget(self.qline_edit_role, 1, 2, 1, 1)

        self.qline_edit_log_path = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_log_path.setObjectName("qline_edit_log_path")
        self.gridLayout.addWidget(self.qline_edit_log_path, 2, 2, 1, 1)

        self.qline_edit_is_dirs = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_is_dirs.setObjectName("qline_edit_is_dirs")
        self.gridLayout.addWidget(self.qline_edit_is_dirs, 3, 2, 1, 1)

        self.btn_add = QPushButton(self)
        self.btn_add.setText("添加")
        self.btn_add.setGeometry(QRect(self.x_left_margin_10 + grid_layout_widget_width - self.button_width_60,
                                       self.y_up_margin_10 + grid_layout_widget_heigth + self.y_up_margin_10,
                                       self.button_width_60,
                                       self.button_height_25))

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)

    def btn_add_clicked(self):
        role = self.qline_edit_role.text()
        path_log = self.qline_edit_log_path.text()
        is_dirs = self.qline_edit_is_dirs.text()

        try:
            role = total_roles[role]
        except KeyError:
            self.msg_failed('角色不对,应为以下的其中一种\n{}'.format(total_roles.keys()))
            return

        if path_log == '':
            self.msg_failed('请填写路径')
            return

        if is_dirs == '':
            self.msg_failed('请填写是否文件夹')
            return

        log_path_setting_dict[role][path_log] = is_dirs

        self.sin1.emit()
        self.close()
