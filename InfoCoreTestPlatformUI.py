# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging

from InfoCoreTestPlatformBaseUI import BaseDlg1
from LogCollectTool.LogCollectToolUI import LogCollectToolDlg
from StreamerLicenseTool.StreamerLicenseToolUI import StreamerLicenseToolDlg
from LogCollectTool.LogCollectToolFunctions import read_machine_setting_from_xls
from LogCollectTool.LogCollectToolFunctions import read_log_path_setting_from_xls
from LogCollectTool.LogCollectToolGlobalVars import machine_setting_file
from LogCollectTool.LogCollectToolGlobalVars import log_path_setting_file
from TimeCalibrationTool.TimeCalibrationToolUI import TimeCalibrationToolDlg
from TimeCalibrationTool.TimeCalibrationToolFunctions import read_time_calibration_machine_setting_from_xls
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_calibration_machine_setting_file
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_calibration_machine_setting_dict
import TimeCalibrationTool.gol
from PortTestTool.PortTestToolUI import PortTestToolDlg

logger = logging.getLogger('root.LogCollectToolUI')

#主窗口-InfoCore测试平台
class MainWindows(QMainWindow):
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(MainWindows,self).__init__(parent)
        self.init_ui()
        self.connect_all_signal_slot()
        self.start_monitor_ui_thread()
        #self.default_set()

    def init_ui(self):
        self.setObjectName("MainWindow")
        self.resize(140, 240)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('InfoCore测试')

        x_margin = 10  # x轴页边距
        y_margin = 10  # y轴页边距
        button_width1 = 120 # 按钮宽度1
        button_width2 = 60  # 按钮宽度2
        button_height = 25  # 按钮高度
        row_spacing = 10    # 行间距
        col_spacing = 10    # 列间距

        i = 0
        self.btn_log_collect_tool = QPushButton(self)  # 按钮-日志收集工具
        self.btn_log_collect_tool.setGeometry(QRect(x_margin,
                                                    y_margin + i * (button_height + row_spacing),
                                                    button_width1,
                                                    button_height))
        self.btn_log_collect_tool.setText('日志收集工具')

        i = i + 1
        self.btn_streamer_license_tool = QPushButton(self)  # 按钮-Streamer在线授权
        self.btn_streamer_license_tool.setGeometry(QRect(x_margin,
                                                          y_margin + i * (button_height + row_spacing),
                                                          button_width1,
                                                          button_height))
        self.btn_streamer_license_tool.setText('Streamer在线授权')

        i = i + 1
        self.btn_time_calibration = QPushButton(self)  # 按钮-时间校准
        self.btn_time_calibration.setGeometry(QRect(x_margin,
                                                          y_margin + i * (button_height + row_spacing),
                                                          button_width1,
                                                          button_height))
        self.btn_time_calibration.setText('时间校准')

        i = i + 1
        self.btn_port_test = QPushButton(self)  # 按钮-端口测试
        self.btn_port_test.setGeometry(QRect(x_margin,
                                             y_margin + i * (button_height + row_spacing),
                                             button_width1,
                                             button_height))
        self.btn_port_test.setText('端口测试')

        i = i + 1
        self.btn_computer_power_control = QPushButton(self) #按钮-服务器电源控制
        self.btn_computer_power_control.setGeometry(QRect(x_margin,
                                                          y_margin + i * (button_height + row_spacing),
                                                          button_width1,
                                                          button_height))
        self.btn_computer_power_control.setText('服务器电源控制')


        i = i + 1
        self.btn_streamer_smoke_testing = QPushButton(self)  # 按钮-Streamer冒烟测试
        self.btn_streamer_smoke_testing.setGeometry(QRect(x_margin,
                                                          y_margin + i * (button_height + row_spacing),
                                                          button_width1,
                                                          button_height))
        self.btn_streamer_smoke_testing.setText('Streamer冒烟测试')

    def connect_all_signal_slot(self):
        self.btn_streamer_smoke_testing.clicked.connect(self.btn_streamer_smoke_testing_clicked)
        self.btn_log_collect_tool.clicked.connect(self.btn_log_collect_tool_clicked)
        self.btn_streamer_license_tool.clicked.connect(self.btn_streamer_license_tool_clicked)
        self.btn_time_calibration.clicked.connect(self.btn_time_calibration_clicked)
        self.btn_port_test.clicked.connect(self.btn_port_test_clicked)

    def btn_port_test_clicked(self):
        port_test_dlg = PortTestToolDlg(self)
        logging.info('打开端口测试对话框')
        port_test_dlg.show()

    def btn_time_calibration_clicked(self):
        TimeCalibrationTool.gol._init() #初始化全局变量
        logging.info('读取时间校准-服务器配置文件')
        if not read_time_calibration_machine_setting_from_xls(time_calibration_machine_setting_file):
            self.msg_failed('读取配置文件失败')
            return
        TimeCalibrationTool.gol.set_value('refresh',len(time_calibration_machine_setting_dict))
        time_calibration_tool_dlg = TimeCalibrationToolDlg(self)
        logging.info('打开时间校准对话框')
        time_calibration_tool_dlg.show()

    def btn_streamer_license_tool_clicked(self):
        streamer_license_tool_dlg = StreamerLicenseToolDlg(self)
        logging.info('打开Streamer在线授权对话框')
        streamer_license_tool_dlg.show()

    def btn_streamer_smoke_testing_clicked(self):
        streamer_smoke_testing_dlg = StreamerSmokeTestingDlg(self)
        logging.info('打开Streamer冒烟测试对话框')
        streamer_smoke_testing_dlg.show()

    def btn_log_collect_tool_clicked(self):
        logging.info('读取日志收集工具-服务器配置文件')
        if not read_machine_setting_from_xls(machine_setting_file):
            self.msg_failed('读取配置文件失败')
            return
        logging.info('读取日志收集工具-收集路径配置文件')
        if not read_log_path_setting_from_xls(log_path_setting_file):
            self.msg_failed('读取配置文件失败')
            return

        log_collect_tool_dlg = LogCollectToolDlg(self)
        logging.info('打开日志收集工具对话框')
        log_collect_tool_dlg.show()

    def start_monitor_ui_thread(self):
        pass

    def msg_success(self,msg_info):
        reply = QMessageBox.information(self,
                                        "结果",
                                        msg_info,
                                        QMessageBox.Yes)

    def msg_failed(self,msg_info):
        reply = QMessageBox.warning(self,
                                    "结果",
                                    msg_info,
                                    QMessageBox.Yes)

#对话框-Streamer冒烟测试
class StreamerSmokeTestingDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(StreamerSmokeTestingDlg,self).__init__(parent)
        self.init_ui()
        self.connect_all_signal_slot()

    def init_ui(self):
        self.resize(150, 200)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.setWindowTitle('Streamer冒烟测试')

        i = 0
        self.btn_setting_test_machine = QPushButton(self)   #按钮-配置待测试服务器
        self.btn_setting_test_machine.setGeometry(QRect(self.x_left_margin_10,
                                                        self.y_up_margin_10 + i * (self.button_height_25 + self.row_spacing_10),
                                                        self.button_width_120,
                                                        self.button_height_25))
        self.btn_setting_test_machine.setText('配置待测试服务器')

        i = i + 1
        self.btn_setting_and_install_dep_package = QPushButton(self)    #按钮-配置并安装依赖包
        self.btn_setting_and_install_dep_package.setGeometry(QRect(self.x_left_margin_10,
                                                                   self.y_up_margin_10 + i * (self.button_height_25 + self.row_spacing_10),
                                                                   self.button_width_120,
                                                                   self.button_height_25))
        self.btn_setting_and_install_dep_package.setText('配置并安装依赖包')

        i = i + 1
        self.btn_install_and_check = QPushButton(self)  #按钮-安装软件并检查结果
        self.btn_install_and_check.setGeometry(QRect(self.x_left_margin_10,
                                                     self.y_up_margin_10 + i * (self.button_height_25 + self.row_spacing_10),
                                                     self.button_width_120,
                                                     self.button_height_25))
        self.btn_install_and_check.setText('安装软件并检查结果')

    def connect_all_signal_slot(self):
        self.btn_setting_test_machine.clicked.connect(self.btn_setting_test_machine_clecked)
        self.btn_setting_and_install_dep_package.clicked.connect(self.btn_setting_and_install_dep_package_clicked)
        self.btn_install_and_check.clicked.connect(self.btn_install_and_check_clicked)

    def btn_setting_test_machine_clecked(self):
        setting_test_machine_dlg = SettingTestMachineDlg(self)
        setting_test_machine_dlg.show()

    def btn_setting_and_install_dep_package_clicked(self):
        print(333)

    def btn_install_and_check_clicked(self):
        print(444)

#对话框-配置待测试服务器
class SettingTestMachineDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(SettingTestMachineDlg,self).__init__(parent)
        self.init_ui()
        self.connect_all_signal_slot()

    def init_ui(self):
        self.resize(250, 200)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        self.setWindowTitle('配置待测试服务器')

        i = 0
        self.btn_show_machine_setting = QPushButton(self)
        self.btn_show_machine_setting.setGeometry(QRect(self.x_left_margin_2,
                                                        self.y_up_margin_10 + i * (self.button_height_25 + self.row_spacing_10),
                                                        self.button_width_120,
                                                        self.button_height_25))
        self.btn_show_machine_setting.setText('查看待测服务器配置')

        i = i + 1
        self.btn_add_machine = QPushButton(self)
        self.btn_add_machine.setGeometry(QRect(self.x_left_margin_2,
                                               self.y_up_margin_10 + i * (self.button_height_25 + self.row_spacing_10),
                                               self.button_width_120,
                                               self.button_height_25))
        self.btn_add_machine.setText('添加服务器')

    def connect_all_signal_slot(self):
        pass





