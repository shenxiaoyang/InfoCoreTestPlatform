# -*- coding:utf-8 -*-
import os
import logging.config
import sys
from PyQt5 import QtWidgets

#可能解决一个不能import backend的BUG
#不知道为什么，pyinstall做出来的exe，某些环境运行的时候，会出现import backend error
from cryptography.hazmat.backends.openssl.backend import backend
x = backend

from InfoCoreTestPlatformGlobalVars import run_path
from LogCollectTool.LogCollectToolGlobalVars import parameters_setting_file,parameters_setting_dict
from InfoCoreTestPlatformFunctions import clean_logs
from InfoCoreTestPlatformUI import MainWindows
from LogCollectTool.LogCollectToolFunctions import read_parameters_setting_from_xls

#创建..\log\ 日志文件夹
if not os.path.exists(r'{}\log'.format(run_path)):
    os.makedirs(r'{}\log'.format(run_path))
clean_logs()    #清理日志
logging.config.fileConfig(r'{}\config\logger.conf'.format(run_path))    #加载日志配置文件
logger = logging.getLogger('root.main') #创建日志对象

#主函数入口
if __name__ == "__main__":
    try:
        logging.info('读取配置...')
        logging.info('读取参数配置文件')
        read_parameters_setting_from_xls(parameters_setting_file)
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindows() #实例化主窗口
        logging.info('打开主窗口-InfoCore测试平台')
        main_window.show()
        sys.exit(app.exec_())
    except BaseException:
        logging.exception('未知错误')

