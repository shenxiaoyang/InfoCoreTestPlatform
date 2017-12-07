# -*- coding:utf-8 -*-
import os
import sys

#运行路径
global run_path
run_path = os.path.dirname(os.path.abspath(sys.argv[0])) #exe程序所在路径

global total_roles
total_roles = {'StreamerServer':'StreamerServer',
               'StreamerLinuxClient':'StreamerLinuxClient',
               'StreamerWindowsClient':'StreamerWindowsClient',
               'LocalStreamerConsole': 'LocalStreamerConsole'}

global total_os_types
total_os_types = {'Windows':'Windows',
                  'Linux':'Linux'}
#global EVENT    #线程阻塞事件
#EVENT = threading.Event()