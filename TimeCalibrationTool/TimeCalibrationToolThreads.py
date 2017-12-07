# -*- coding:utf-8 -*-
import threading
import logging
from InfoCoreTools.Time import get_windows_time_str
from InfoCoreTools.Time import get_linux_time_str
from InfoCoreTools.Time import get_beijin_time_str
from InfoCoreTools.Time import get_local_time_str
from InfoCoreTools.Time import set_linux_time
from InfoCoreTools.Time import set_windows_time
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_dict
from TimeCalibrationTool.TimeCalibrationToolGlobalVars import TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT

logger = logging.getLogger('root.TimeCalibrationTool.TimeCalibrationToolThread')

class GetWindowsTimeStrThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password,thread_name=None, parent=None):
        super(GetWindowsTimeStrThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.username = username
        self.password = password

    def run(self):
        logging.info('获取{}时间字符串[Windows]'.format(self.ip))
        windows_time_str = get_windows_time_str(self.ip,self.username,self.password)[0]
        logging.info('{}系统时间获取完毕[windows]'.format(self.ip))
        time_dict[self.ip] = windows_time_str
        TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()

class GetLinuxTimeStrThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password,thread_name=None, parent=None):
        super(GetLinuxTimeStrThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.username = username
        self.password = password

    def run(self):
        logging.info('获取{}时间字符串[Linux]'.format(self.ip))
        linux_time_str = get_linux_time_str(self.ip,self.username,self.password)[0]
        logging.info('{}系统时间获取完毕[Linux]'.format(self.ip))
        time_dict[self.ip] = linux_time_str
        TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()

class GetBeijinTimeStrThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, thread_name=None, parent=None):
        super(GetBeijinTimeStrThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name

    def run(self):
        logging.info('获取北京时间字符串')
        beijin_time_str = get_beijin_time_str()[0]
        logging.info('北京时间获取完毕')
        time_dict['北京时间'] = beijin_time_str
        TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()


class GetLocalTimeStrThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, thread_name=None, parent=None):
        super(GetLocalTimeStrThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name

    def run(self):
        logging.info('获取本地时间字符串')
        local_time_str = get_local_time_str()[0]
        logging.info('本地时间获取完毕')
        time_dict['本地时间'] = local_time_str
        TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()

class SetLinuxTimeThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password, time_str ,thread_name=None, parent=None):
        super(SetLinuxTimeThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.username = username
        self.password = password
        self.time_str = time_str

    def run(self):
        logging.info('准备设置{}系统时间->{}'.format(self.ip,self.time_str))
        set_linux_time(self.ip,self.username,self.password,self.time_str)
        logging.info('{}系统时间设置完毕'.format(self.ip))
        #TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()

class SetWindowsTimeThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password, time_str ,thread_name=None, parent=None):
        super(SetWindowsTimeThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.username = username
        self.password = password
        self.time_str = time_str

    def run(self):
        logging.info('准备设置{}系统时间->{}'.format(self.ip,self.time_str))
        set_windows_time(self.ip,self.username,self.password,self.time_str)
        logging.info('{}系统时间设置完毕'.format(self.ip))
        #TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT.set()
