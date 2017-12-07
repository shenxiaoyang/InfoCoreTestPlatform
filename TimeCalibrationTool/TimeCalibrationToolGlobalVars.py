# -*- coding:utf-8 -*-
import collections
import threading

from StreamerTestPlatformGlobalVars import run_path

global time_calibration_machine_setting_dict
time_calibration_machine_setting_dict = collections.OrderedDict()

#服务器配置信息文件地址
global time_calibration_machine_setting_file
time_calibration_machine_setting_file = r'{}\config\time_calibration_machine_setting.xls'.format(run_path)

global TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT #线程阻塞事件
TIME_CALIBRATION_TOOL_BACKGROUND_DATA_UPDATE_EVENT = threading.Event()

global time_dict
time_dict = collections.OrderedDict()

global local_time_diff_dict
local_time_diff_dict = collections.OrderedDict()

global beijin_time_diff_dict
beijin_time_diff_dict = collections.OrderedDict()