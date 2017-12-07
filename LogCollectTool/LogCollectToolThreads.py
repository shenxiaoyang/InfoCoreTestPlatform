# -*- coding:utf-8 -*-
import threading
import time
import logging
import os
from subprocess import run

logger = logging.getLogger('root.Threads')
from LogCollectTool.LogCollectToolGlobalVars import LOG_COLLECT_TOOL_UI_UPDATE_EVENT
from InfoCoreTools import FileCopy,WindowsCMD

class CopyLinuxFileThread(threading.Thread):
    #daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password, remote_file, local_path, thread_name=None, parent=None):
        super(CopyLinuxFileThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.port = 22
        self.username = username
        self.password = password
        self.remote_file = remote_file
        self.local_path = local_path

    def run(self):
        for path in self.remote_file:
            FileCopy.download_file(self.ip,
                                   self.port,
                                   self.username,
                                   self.password,
                                   path,
                                   self.local_path)

class CopyWindowsFileThread(threading.Thread):
    #daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, ip, username, password, remote, local, thread_name=None, parent=None):
        super(CopyWindowsFileThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.ip = ip
        self.username = username
        self.password = password
        self.remote_file = remote
        self.local_path = local

    def run(self):
        for path in self.remote_file:
            if self.remote_file[path] == '否':
                FileCopy.win_download_file(self.ip,
                                           self.username,
                                           self.password,
                                           path,
                                           self.local_path)
            elif self.remote_file[path] == '是':
                FileCopy.win_download_dir(self.ip,
                                           self.username,
                                           self.password,
                                           path,
                                           self.local_path)
            else:
                logging.error('log_path_config配置文件中参数【是否文件夹】配置错误')
                exit(1)

class CopyLocalStreamerConsoleFileThread(threading.Thread):
    #daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, remote, local, thread_name=None, parent=None):
        super(CopyLocalStreamerConsoleFileThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.remote_file = remote
        self.local_path = local

    def run(self):
        try:
            for path in self.remote_file:
                if self.remote_file[path] == '否':
                    logging.info('拷贝文件->{}'.format(path))
                    run(r'xcopy "{}"  "{}" /e /y 2>nul 1>nul'.format(path, self.local_path), shell=True)
                elif self.remote_file[path] == '是':
                    child_dir = os.path.split(path)
                    if child_dir[1] == '':  # 目录的最后有/。
                        child_dir = os.path.split(child_dir[0])
                        remote = path + '*.*'
                    else:
                        remote = path + '/*.*'
                    local = self.local_path + '/' + child_dir[1]
                    if not os.path.exists(local):
                        os.makedirs(local)
                    run(r'xcopy "{}"  "{}" /e /y 2>nul 1>nul'.format(remote,local), shell=True)
                else:
                    logging.error('log_path_config配置文件中参数【是否文件夹】配置错误')
                    exit(1)
        except BaseException:
            logging.exception('未知错误')

class ThreadNumCheckThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, thread_name=None, parent=None):
        super(ThreadNumCheckThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name

    def run(self):
        while 1:
            logging.info('正在收集日志的线程有{}个'.format(threading.active_count()-2))
            if threading.active_count() == 2:
                LOG_COLLECT_TOOL_UI_UPDATE_EVENT.set()
                break
            time.sleep(1)

