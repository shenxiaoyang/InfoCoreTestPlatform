# -*- coding:utf-8 -*-
import collections
import threading

from InfoCoreTestPlatformGlobalVars import run_path

global machine_power_control_setting_dict
machine_power_control_setting_dict = collections.OrderedDict()

#服务器配置信息文件地址
global machine_power_control_setting_file
machine_power_control_setting_file = r'{}\config\machine_power_control_setting.xls'.format(run_path)