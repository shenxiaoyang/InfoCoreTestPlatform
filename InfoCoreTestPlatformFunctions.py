# -*- coding:utf-8 -*-
import os
from InfoCoreTestPlatformGlobalVars import run_path

def clean_logs():
    streamer_install_log_path = r'{}\install_log'.format(run_path)
    tool_log_path = r'{}\log'.format(run_path)
    for root,dirs,files in os.walk(streamer_install_log_path):
        for file_name in files:
            file = r'{}\{}'.format(streamer_install_log_path, file_name)
            if os.path.exists(file):
                os.remove(file)
    for root,dirs,files in os.walk(tool_log_path):
        for file_name in files:
            file = r'{}\{}'.format(tool_log_path, file_name)
            if os.path.exists(file):
                os.remove(file)