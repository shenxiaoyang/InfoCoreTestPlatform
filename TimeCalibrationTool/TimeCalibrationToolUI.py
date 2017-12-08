# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging

logger = logging.getLogger('root.TimeCalibrationTool.TimeCalibrationToolUI')

from InfoCoreTestPlatformBaseUI import BaseDlg1
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_calibration_machine_setting_dict
from TimeCalibrationTool.TimeCalibrationToolClass import TimeCalibrationToolMachine
from InfoCoreTestPlatformGlobalVars import total_os_types
from TimeCalibrationTool.TimeCalibrationToolFunctions import save_time_calibration_machine_setting_to_xls
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_calibration_machine_setting_file
from InfoCoreTools.Time import time_minus
from InfoCoreTools.Time import get_linux_time_str
from InfoCoreTools.Time import get_beijin_time_str
from InfoCoreTools.Time import get_windows_time_str
from InfoCoreTools.Time import get_local_time_str
from InfoCoreTools.Time import set_linux_time
from InfoCoreTools.Time import set_windows_time
from InfoCoreTools.WindowsCMD import pingIP
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT
import TimeCalibrationTool.gol
from TimeCalibrationTool.TimeCalibrationToolThreads import GetBeijinTimeStrThread
from TimeCalibrationTool.TimeCalibrationToolThreads import GetLocalTimeStrThread
from TimeCalibrationTool.TimeCalibrationToolThreads import GetLinuxTimeStrThread
from TimeCalibrationTool.TimeCalibrationToolThreads import GetWindowsTimeStrThread
from TimeCalibrationTool.TimeCalibrationToolThreads import SetLinuxTimeThread
from TimeCalibrationTool.TimeCalibrationToolThreads import SetWindowsTimeThread
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import local_time_diff_dict
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import beijin_time_diff_dict
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_dict



#监控线程，主要用于监控界面是否有更新，如果有更新，则刷新相应的界面
class TimeCalibrationToolMonitorUIThread(QThread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    signal_update_time_calibration_tool_table = pyqtSignal()  # 自定义信号

    def __init__(self, event ,parent=None):
        super(TimeCalibrationToolMonitorUIThread, self).__init__(parent)
        self.event = event

    def run(self):
        i = 0
        while 1:
            self.event.wait()   #阻塞线程，等待外部事件响应
            i = i + 1
            try:
                for ip in time_calibration_machine_setting_dict:
                    logging.info('---计算{}的时间差start---[count:{}]'.format(ip,i))
                    local_time_diff_dict[ip] = time_minus(time_dict['本地时间'],time_dict[ip])
                    beijin_time_diff_dict[ip] = time_minus(time_dict['北京时间'],time_dict[ip])
                    logging.info('---计算{}的时间差end---[count:{}]'.format(ip,i))
                self.signal_update_time_calibration_tool_table.emit()  # 发射信号
            except BaseException:
                logging.exception('未知错误')
            self.event.clear()  #重新设置线程阻塞

#时间校准对话框
class TimeCalibrationToolDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(TimeCalibrationToolDlg, self).__init__(parent)
        self.start_monitor_ui_thread()

    def init_ui(self):
        self.setWindowTitle('时间校准')  # 设置窗口标题

        self.btn_add = QPushButton(self)
        self.btn_add.setText('添加')

        self.btn_delete = QPushButton(self)
        self.btn_delete.setText('删除')
        self.btn_delete.setDisabled(True)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')

        self.btn_refresh = QPushButton(self)
        self.btn_refresh.setText('刷新')

        self.comboBox_time_tpye = QComboBox(self)
        self.comboBox_time_tpye.addItem("北京时间")
        self.comboBox_time_tpye.addItem("本机时间")

        self.btn_calibration = QPushButton(self)
        self.btn_calibration.setText('校准')

        self.table = QTableWidget(self)  # 创建表
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止拖动列宽
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 按行选择模式
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择模式
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止修改单元格内容
        self.table.setAlternatingRowColors(True)  # 隔行变色

        self.init_background_data()
        self.refresh_ui()

    def init_background_data(self):
        time_dict['北京时间'] = '北京时间未获取'
        time_dict['本地时间'] = '本地时间未获取'
        for ip in time_calibration_machine_setting_dict:
            time_dict[ip] = '请按刷新按钮刷新时间'
            local_time_diff_dict[ip] = '请按刷新按钮刷新时间'
            beijin_time_diff_dict[ip] = '请按刷新按钮刷新时间'

    def refresh_layout(self):
        try:
            logging.info("界面控件布局")
            x = 0
            y = 0
            self.btn_add.setGeometry(QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
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
            self.btn_save.setGeometry(QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
                                            self.y_up_margin_2,
                                            self.button_width_50,
                                            self.button_height_25))

            x = x + 1
            y = y + 1
            self.btn_refresh.setGeometry(
                QRect(self.x_left_margin_2 + self.button_width_50 * x + self.widget_width_space_5 * y,
                      self.y_up_margin_2,
                      self.button_width_50,
                      self.button_height_25))

            self.table.resizeColumnsToContents()  # 设置自适应列宽
            self.table.resizeRowsToContents()  # 设置自适应行高
            col_width = 0  # 表格总宽
            for j in range(self.table.columnCount()):
                col_width = col_width + self.table.columnWidth(j)
            #col_width = col_width + 2  # 表格和表格桌布预留空间

            row_heigth = 0  # 表格总高(不含表头高度)
            for k in range(len(time_calibration_machine_setting_dict)):
                row_heigth = row_heigth + self.table.rowHeight(k)

            min_width = self.x_left_margin_2 * 2 + self.button_width_50 * 5 + self.button_width_80 + self.widget_width_space_5 * 4
            if col_width < min_width:
                col_width = min_width
                #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setGeometry(QRect(self.x_left_margin_2,  #左边空余2个尺度
                                         self.y_up_margin_2 + self.button_height_25 + self.widget_heigth_space_5,    #上面空余2个尺度+一个按钮25尺度+5尺度控件间距
                                         col_width,
                                         row_heigth + self.table_head_heigth))
            self.resize(col_width + 2 * self.x_left_margin_2,
                        row_heigth + self.table_head_heigth + 2 * self.y_up_margin_2 + self.button_height_25 + self.widget_heigth_space_5)  # 设置窗口大小

            self.comboBox_time_tpye.setGeometry(QRect(col_width + self.x_left_margin_2 - self.button_width_50 - self.widget_width_space_5 - self.button_width_80,
                                                      self.y_up_margin_2+1,
                                                      self.button_width_80,
                                                      self.button_height_25-2))
            self.btn_calibration.setGeometry(QRect(col_width + self.x_left_margin_2 - self.button_width_50,
                                                   self.y_up_margin_2,
                                                   self.button_width_50,
                                                   self.button_height_25))
            logging.info('界面控件布局结束')
        except BaseException:
            logging.exception('未知错误')

    def refresh_ui(self):
        try:
            logging.info("刷新界面数据")
            self.table.setColumnCount(5)
            self.table.setRowCount(len(time_calibration_machine_setting_dict))

            logging.info('设置表头')
            horizontalHeader = ["操作系统", "IP", "用户名", "密码", "时差"]
            self.table.setHorizontalHeaderLabels(horizontalHeader)
            logging.info('设置表内容')
            i = 0
            for ip in time_calibration_machine_setting_dict:
                server = time_calibration_machine_setting_dict[ip]
                self.table.setItem(i, 0, QTableWidgetItem(server.os_type))
                self.table.setItem(i, 1, QTableWidgetItem(server.ip_address))
                self.table.setItem(i, 2, QTableWidgetItem(server.username))
                self.table.setItem(i, 3, QTableWidgetItem(server.password))
                try:
                    standard_time_str = self.comboBox_time_tpye.currentText()
                    if standard_time_str == '北京时间':
                        time_str = beijin_time_diff_dict[ip]
                    else:
                        time_str = local_time_diff_dict[ip]
                except KeyError:
                    self.table.setItem(i, 4, QTableWidgetItem('{}获取失败'.format(standard_time_str)))
                    i = i + 1
                    continue

                if type(time_str) == str:
                    self.table.setItem(i, 4, QTableWidgetItem(time_str))
                elif time_str >= 0:
                    self.table.setItem(i, 4, QTableWidgetItem('比{}慢{}秒'.format(standard_time_str,time_str)))
                else:
                    self.table.setItem(i, 4, QTableWidgetItem('比{}快{}秒'.format(standard_time_str,-time_str)))

                i = i + 1
            logging.info('表内容布置完毕')
            self.refresh_layout()  # 设置控件布局
        except BaseException:
            logging.exception('未知错误')

    def start_monitor_ui_thread(self):
        logging.info('启动时间校准工具后台刷新监控线程')
        self.time_calibration_tool_monitor_ui_thread = TimeCalibrationToolMonitorUIThread(TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT)    #注册事件器
        self.time_calibration_tool_monitor_ui_thread.start()  #启动线程
        self.time_calibration_tool_monitor_ui_thread.signal_update_time_calibration_tool_table.connect(self.refresh_ui)

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn_delete.clicked.connect(self.btn_delete_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.comboBox_time_tpye.currentIndexChanged.connect(self.comboBox_time_tpye_changed)
        self.btn_calibration.clicked.connect(self.btn_calibration_clicked)
        self.btn_refresh.clicked.connect(self.btn_refresh_clicked)

    def btn_refresh_clicked(self):
        #self.btn_add.setDisabled(True)
        #self.btn_delete.setDisabled(True)
        #self.btn_refresh.setDisabled(True)
        #self.btn_calibration.setDisabled(True)
        #self.comboBox_time_tpye.setDisabled(True)
        self.refresh_back_data()
        self.msg_success('刷新成功，Windows服务器获取信息教慢，请耐心等待')

    def btn_calibration_clicked(self):
        logging.info('准备校准时间')
        time_type = self.comboBox_time_tpye.currentText()
        logging.info('基准时间为：{}'.format(time_type))
        if time_type == '北京时间':
            time_str = get_beijin_time_str()[0]
        else:
            time_str = get_local_time_str()[0]
        for ip_address in time_calibration_machine_setting_dict:
            server = time_calibration_machine_setting_dict[ip_address]
            if pingIP(ip_address) == 0:
                if server.os_type == 'Windows':
                    set_windows_time_thread=SetWindowsTimeThread(server.ip_address,
                                                                 server.username,
                                                                 server.password,
                                                                 time_str)
                    set_windows_time_thread.start()
                elif server.os_type == 'Linux':
                    set_linux_time_thread=SetLinuxTimeThread(server.ip_address,
                                                             server.username,
                                                             server.password,
                                                             time_str)
                    set_linux_time_thread.start()
                else:
                    logging.warning('{}系统还不支持时间校准'.format(server.os_type))
            else:
                logging.warning('{}PING不通'.format(ip_address))
        self.msg_success('校准成功!\nWindows服务器设置操作需要40s左右...耐心等等....')
        #self.refresh_back_data()

    def comboBox_time_tpye_changed(self):
        self.refresh_back_data()

    def btn_save_clicked(self):
        if save_time_calibration_machine_setting_to_xls(time_calibration_machine_setting_file):
            self.msg_success('保存成功')
        else:
            self.msg_success('保存失败')

    def table_clicked(self):
        self.btn_delete.setEnabled(True)

    def btn_delete_clicked(self):
        try:
            select_row = self.table.currentRow()
            select_ip = self.table.item(select_row,1).text()
            time_calibration_machine_setting_dict.pop(select_ip)
            time_dict.pop(select_ip)
            beijin_time_diff_dict.pop(select_ip)
            local_time_diff_dict.pop(select_ip)
            self.refresh_ui()
        except BaseException:
            logging.exception('未知错误')

    def btn_add_clicked(self):
        add_time_calibration_machine_dlg = AddTimeCalibrationToolMachineSetting(self)
        add_time_calibration_machine_dlg.show()
        add_time_calibration_machine_dlg.sin1.connect(self.add_new_data)

    def add_new_data(self):
        self.init_background_data()
        self.refresh_ui()

    def refresh_back_data(self):
        try:
            #TimeCalibrationTool.gol.set_value('refresh',len(time_calibration_machine_setting_dict)+2)
            logging.info("开始刷新后台数据")
            logging.info('启动获取北京时间线程')
            get_beijin_time_str_thread = GetBeijinTimeStrThread()
            get_beijin_time_str_thread.start()
            logging.info('启动获取本地时间线程')
            get_local_time_str_thread = GetLocalTimeStrThread()
            get_local_time_str_thread.start()
            for ip in time_calibration_machine_setting_dict:
                server = time_calibration_machine_setting_dict[ip]
                if pingIP(server.ip_address) == 0:
                    beijin_time_diff_dict[ip] = '正在获取......'
                    local_time_diff_dict[ip] = '正在获取......'
                    time_dict[ip] = '正在获取......'
                    if server.os_type == 'Linux':
                        logging.info('启动获取{}系统时间线程'.format(server.ip_address))
                        get_linux_time_str_thread = GetLinuxTimeStrThread(server.ip_address,
                                                                          server.username,
                                                                          server.password)
                        get_linux_time_str_thread.start()
                    elif server.os_type == 'Windows':
                        logging.info('启动获取{}系统时间线程'.format(server.ip_address))
                        get_windows_time_str_thread = GetWindowsTimeStrThread(server.ip_address,
                                                                              server.username,
                                                                              server.password)
                        get_windows_time_str_thread.start()
                    else:
                        time_dict[server.ip_address] = '操作系统类型不对'
                        TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()
                        logging.warning('操作系统类型不对')
                else:
                    time_dict[server.ip_address] = 'IP地址PING不通'
                    TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()
                    logging.warning('IP地址PING不通')
        except BaseException:
            logging.exception('未知错误')

class AddTimeCalibrationToolMachineSetting(BaseDlg1):
    sin1 = pyqtSignal()  # 自定义信号
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(AddTimeCalibrationToolMachineSetting,self).__init__(parent)

    def init_ui(self):
        self.setWindowTitle('添加服务器')  # 设置窗口标题
        self.resize(200,
                    self.y_up_margin_10 + self.button_height_25 * 4 + self.y_up_margin_10 + self.button_height_25 + self.y_up_margin_10)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        grid_layout_widget_width = 180
        grid_layout_widget_heigth = self.button_height_25 * 4

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
        i = 0

        i= i +1
        self.label_os_type = QLabel(self.gridLayoutWidget_1)
        self.label_os_type.setObjectName("label_os_type")
        self.gridLayout.addWidget(self.label_os_type, i, 1)
        self.label_os_type.setText('操作系统')

        i = i + 1
        self.label_ip_address = QLabel(self.gridLayoutWidget_1)
        self.label_ip_address.setObjectName("label_ip_address")
        self.gridLayout.addWidget(self.label_ip_address, i, 1)
        self.label_ip_address.setText('IP地址')

        i = i + 1
        self.label_username = QLabel(self.gridLayoutWidget_1)
        self.label_username.setObjectName("label_username")
        self.gridLayout.addWidget(self.label_username, i, 1)
        self.label_username.setText('用户名')

        i = i + 1
        self.label_password = QLabel(self.gridLayoutWidget_1)
        self.label_password.setObjectName("label_password")
        self.gridLayout.addWidget(self.label_password, i, 1)
        self.label_password.setText('密码')

        # 界面上个各个文本编辑框布局
        i = 0

        i = i + 1
        self.qline_edit_os_type = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_os_type.setObjectName("qline_edit_os_type")
        self.gridLayout.addWidget(self.qline_edit_os_type, i, 2, 1, 1)

        i = i + 1
        self.qline_edit_ip_address = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_ip_address.setObjectName("qline_edit_ip_address")
        self.gridLayout.addWidget(self.qline_edit_ip_address, i, 2, 1, 1)

        i = i + 1
        self.qline_edit_username = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_username.setObjectName("qline_edit_username")
        self.gridLayout.addWidget(self.qline_edit_username, i, 2, 1, 1)

        i = i + 1
        self.qline_edit_password = QLineEdit(self.gridLayoutWidget_1)
        self.qline_edit_password.setObjectName("qline_edit_password")
        self.gridLayout.addWidget(self.qline_edit_password, i, 2, 1, 1)

        self.btn_add = QPushButton(self)
        self.btn_add.setText("添加")
        self.btn_add.setGeometry(QRect(self.x_left_margin_10 + grid_layout_widget_width - self.button_width_60,
                                       self.y_up_margin_10 + grid_layout_widget_heigth + self.y_up_margin_10,
                                       self.button_width_60,
                                       self.button_height_25))

    def connect_all_signal_slot(self):
        self.btn_add.clicked.connect(self.btn_add_clicked)

    def btn_add_clicked(self):
        os_type = self.qline_edit_os_type.text()
        ip_address = self.qline_edit_ip_address.text()
        username = self.qline_edit_username.text()
        password = self.qline_edit_password.text()

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

        new_server = TimeCalibrationToolMachine()
        new_server.os_type = os_type
        new_server.ip_address = ip_address
        new_server.username = username
        new_server.password = password
        time_calibration_machine_setting_dict[ip_address] = new_server

        self.sin1.emit()
        self.close()