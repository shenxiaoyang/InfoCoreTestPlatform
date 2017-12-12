# -*- coding:utf-8 -*-
import logging
import xlrd
import os
import xlwt

logger = logging.getLogger('root.ComputerPowerControlTool.ComputerPowerControlToolFunctions')

from ComputerPowerControlTool.ComputerPowerControlToolGlobalVals import machine_power_control_setting_dict
from ComputerPowerControlTool.ComputerPowerControlToolClass import ComputerPowerControlMachine

def read_power_control_machine_setting_from_xls(file_name):
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
        computer_type = sheet.cell(row, 0).value  # 获取获取第X行的第1列，即设备类型
        os_type = sheet.cell(row, 1).value  # 获取获取第X行的第2列，即操作系统
        ip_address = sheet.cell(row, 2).value  # 获取获取第X行的第3列，即IP地址
        username = sheet.cell(row, 3).value  # 获取获取第X行的第4列，即用户名
        password = sheet.cell(row, 4).value # 获取获取第X行的第5列，即密码
        if sheet.cell(row, 5).value == '是':
            is_ipmi_enabled = True
        elif sheet.cell(row, 5).value == '否':
            is_ipmi_enabled = False
        else:
            logging.error('配置文件{}有错误'.format(file_name))
            exit(1)
        ipmi_ip = sheet.cell(row, 6).value
        ipmi_username = sheet.cell(row, 7).value
        ipmi_password = sheet.cell(row, 8).value
        if sheet.cell(row, 9).value == '是':
            is_vm = True
        elif sheet.cell(row, 9).value == '否':
            is_vm = False
        esxi_ip = sheet.cell(row, 10).value  # 获取获取第X行的第6列，即ESXi IP地址
        esxi_username = sheet.cell(row, 11).value  # 获取获取第X行的第7列，即ESXi 用户名
        esxi_password = sheet.cell(row, 12).value  # 获取获取第X行的第8列，即ESXi 密码
        vm_name = sheet.cell(row, 13).value  # 获取获取第X行的第9列，即虚拟机名

        new_server = ComputerPowerControlMachine()
        new_server.computer_type = computer_type
        new_server.os_type = os_type
        new_server.ip_address = ip_address
        new_server.username = username
        new_server.password = password
        new_server.is_ipmi_enabled = is_ipmi_enabled
        new_server.ipmi_ip = ipmi_ip
        new_server.ipmi_username = ipmi_username
        new_server.ipmi_password = ipmi_password
        new_server.is_vm = is_vm
        new_server.esxi_ip = esxi_ip
        new_server.esxi_username = esxi_username
        new_server.esxi_password = esxi_password
        new_server.vm_name = vm_name
        machine_power_control_setting_dict[ip_address] = new_server
    return True

def save_power_control_machine_setting_to_xls(file_name):
    if not os.path.exists(file_name):
        logging.error('配置文件{}不存在'.format(file_name))
        return False
    try:
        workbook = xlwt.Workbook()  # 创建工作簿
        sheet1 = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
        style1 = set_style('华文细黑', 220, False)
        style2 = set_style('华文细黑', 250, False)
        title_list = ["设备类型","操作系统", "IP", "用户名", "密码","是否启用IPMI","IPMI IP","IPMI用户名","IPMI密码",
                      "是否虚拟机","主机IP","主机用户名","主机密码","虚拟机名称"]
        j = 0
        k = 0
        for key in title_list:
            sheet1.write(j,k,key,style2)
            k = k + 1
        j = j + 1
        for ip_address in machine_power_control_setting_dict:
            server = machine_power_control_setting_dict[ip_address]
            sheet1.write(j, 0, server.computer_type, style1)
            sheet1.write(j, 1, server.os_type, style1)
            sheet1.write(j, 2, server.ip_address, style1)
            sheet1.write(j, 3, server.username, style1)
            sheet1.write(j, 4, server.password, style1)
            if server.is_ipmi_enabled:
                sheet1.write(j, 5, '是', style1)
            else:
                sheet1.write(j, 5, '否', style1)
            sheet1.write(j, 6, server.ipmi_ip, style1)
            sheet1.write(j, 7, server.ipmi_username, style1)
            sheet1.write(j, 8, server.ipmi_password, style1)
            if server.is_vm:
                sheet1.write(j, 9, '是', style1)
            else:
                sheet1.write(j, 9, '否', style1)
            sheet1.write(j, 10, server.esxi_ip, style1)
            sheet1.write(j, 11, server.esxi_username, style1)
            sheet1.write(j, 12, server.esxi_password, style1)
            sheet1.write(j, 13, server.vm_name, style1)
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