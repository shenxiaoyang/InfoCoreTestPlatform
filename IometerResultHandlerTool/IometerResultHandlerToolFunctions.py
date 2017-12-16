# -*- coding:utf-8 -*-
import xlwt
import csv
import os

from IometerResultHandlerTool.IometerResultHanderToolGlobalVals import iometer_data
def read_iometer_data_from_csv(file_name):
    file = open(file_name, 'r')
    reader = csv.reader(file)
    iometer_data = {}
    for line in reader:
        if line[0] == '\'Target Type' and global_vars['title_flag'] == 1:
            title = []
            for data in line:
                title.append(data)
            iometer_data['title'] = title
            global_vars['title_flag'] = 0
        if line[0] == 'ALL':
            data_a = []
            for data in line:
                data_a.append(data)
            iometer_data[line[2]] = data_a
    iometer_data[file_name] = iometer_data