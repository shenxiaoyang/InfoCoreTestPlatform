# -*- coding:utf-8 -*-
import logging
import xlrd
import os
import xlwt

logger = logging.getLogger('root.TimeCalibrationTool.TimeCalibrationToolFunctions')

from TimeCalibrationTool.TimeCalibrationToolGlobalVars import time_calibration_machine_setting_dict
from TimeCalibrationTool.TimeCalibrationToolClass import TimeCalibrationToolMachine

def read_time_calibration_machine_setting_from_xls(file_name):
    logging.debug('从{}中读取配置'.format(file_name))
    if not os.path.exists(file_name):
        logging.error('配置文件{}不存在'.format(file_name))
        return False
    data = xlrd.open_workbook(file_name)  # 打开工作簿
    sheet = data.sheet_by_index(0)  # 获取第一个工作表
    nrows = sheet.nrows  # 获取行数
    ncols = sheet.ncols  # 获取列数
    for row in range(nrows):  # 遍历每一行
        if row == 0:  # 如果是第一行（表头），则舍弃
            continue
        os_type = sheet.cell(row, 0).value  # 获取获取第X行的第1列，即操作系统
        ip_address = sheet.cell(row, 1).value  # 获取获取第X行的第2列，即IP地址
        username = sheet.cell(row, 2).value  # 获取获取第X行的第3列，即用户名
        password = sheet.cell(row, 3).value # 获取获取第X行的第4列，即密码

        new_server = TimeCalibrationToolMachine()
        new_server.os_type = os_type
        new_server.ip_address = ip_address
        new_server.username = username
        new_server.password = password
        time_calibration_machine_setting_dict[ip_address] = new_server
    return True

def save_time_calibration_machine_setting_to_xls(file_name):
    if not os.path.exists(file_name):
        logging.error('配置文件{}不存在'.format(file_name))
        return False
    try:
        workbook = xlwt.Workbook()  # 创建工作簿
        sheet1 = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
        style1 = set_style('华文细黑', 220, False)
        style2 = set_style('华文细黑', 250, False)
        title_list = ["操作系统", "IP", "用户名", "密码"]
        j = 0
        k = 0
        for key in title_list:
            sheet1.write(j,k,key,style2)
            k = k + 1
        j = j + 1
        for ip_address in time_calibration_machine_setting_dict:
            server = time_calibration_machine_setting_dict[ip_address]
            sheet1.write(j, 0, server.os_type, style1)
            sheet1.write(j, 1, server.ip_address, style1)
            sheet1.write(j, 2, server.username, style1)
            sheet1.write(j, 3, server.password, style1)
            j = j + 1

        workbook.save(file_name)
        return True
    except BaseException:
        logging.exception('未知错误')
        return False

def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name    #设置字体
    font.bold = bold    #设置字体是否加粗
    font.color_index = 4
    font.height = height    #设置字体高度

    style.font = font
    return style