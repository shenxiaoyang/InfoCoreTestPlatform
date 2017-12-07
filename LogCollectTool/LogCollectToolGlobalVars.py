# -*- coding:utf-8 -*-
import collections
import threading

from InfoCoreTestPlatformGlobalVars import run_path

#日志收集工具服务器配置信息字典，所有的服务器配置信息都保存在这个字典中
global machine_setting_dict
machine_setting_dict = collections.OrderedDict()

#日志收集工具收集路径配置字典，这个字典包含了需要收集的日志文件地址
global log_path_setting_dict
log_path_setting_dict = collections.OrderedDict()

global parameters_setting_dict
parameters_setting_dict = collections.OrderedDict()

#服务器配置信息文件地址
global machine_setting_file
machine_setting_file = '{}\config\log_collect_tool_machine_setting.xls'.format(run_path)

#自定义日志收集路径配置文件
global log_path_setting_file
log_path_setting_file = '{}\config\log_collect_tool_log_path_setting.xls'.format(run_path)

global parameters_setting_file
parameters_setting_file = '{}\config\parameters_setting.xls'.format(run_path)

global LOG_COLLECT_TOOL_UI_UPDATE_EVENT #线程阻塞事件
LOG_COLLECT_TOOL_UI_UPDATE_EVENT = threading.Event()