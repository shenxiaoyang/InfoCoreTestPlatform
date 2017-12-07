# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import paramiko
import re
import datetime
import socket

from InfoCoreTestPlatformBaseUI import BaseDlg1
from StreamerLicenseTool.StreamerLicenseToolGlobalVars import author_server
from InfoCoreTools.WindowsCMD import pingIP
from InfoCoreTools.SSH import ssh

logger = logging.getLogger('root.StreamerLicenseToolUI')

#在线授权对话框[单个服务器]
class StreamerLicenseToolDlg(BaseDlg1):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(StreamerLicenseToolDlg, self).__init__(parent)
        self.retranslateUi()

    def init_ui(self):
        self.setObjectName("SingleOnlineActiveDlg")
        self.resize(500, 80)  # 设置窗口大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小

        self.horizontalLayoutWidget = QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QRect(20, 20, 460, 20))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_server_ip = QLabel(self.horizontalLayoutWidget)
        self.label_server_ip.setObjectName("label_server_ip")
        self.horizontalLayout.addWidget(self.label_server_ip)
        self.lineEdit_server_ip = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_server_ip.setObjectName("lineEdit_server_ip")
        self.horizontalLayout.addWidget(self.lineEdit_server_ip)
        self.label_username = QLabel(self.horizontalLayoutWidget)
        self.label_username.setObjectName("label_username")
        self.horizontalLayout.addWidget(self.label_username)
        self.label_password = QLabel(self.horizontalLayoutWidget)
        self.label_password.setObjectName("label_password")
        self.horizontalLayout.addWidget(self.label_password)
        self.lineEdit_password = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.horizontalLayout.addWidget(self.lineEdit_password)
        self.label_text = QLabel(self)
        self.label_text.setGeometry(QRect(20, 50, 460, 20))
        self.label_text.setObjectName("label_text")

        self.btn_online_active = QPushButton(self)
        self.btn_online_active.setObjectName("btn_get_authorization")
        self.horizontalLayout.addWidget(self.btn_online_active)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("SingleOnlineActiveDlg", "在线授权"))
        self.label_server_ip.setText(_translate("SingleOnlineActiveDlg", "IP地址"))
        self.label_username.setText(_translate("SingleOnlineActiveDlg", "用户名:root "))
        self.label_password.setText(_translate("SingleOnlineActiveDlg", "密码"))
        self.btn_online_active.setText(_translate("SingleOnlineActiveDlg", "授权"))
        self.label_text.setText(_translate("SingleOnlineActiveDlg", "说明：默认功能全开，测试版60天，客户端12，容量1PB。其他授权请找沈晓阳"))

    def connect_all_signal_slot(self):
        self.btn_online_active.clicked.connect(self.btn_online_active_clicked)

    def btn_online_active_clicked(self):
        logging.info('开始Streamer授权')
        client_server_ip = self.lineEdit_server_ip.text()
        client_username = 'root'
        client_password = self.lineEdit_password.text()

        if client_server_ip == '':
            self.msg_failed("请填写IP地址")
            return
        else:
            #PI地址合法性匹配说明，^行首开始匹配，\d{1,3}匹配1-3个数字，(?:\.\d{1,3}){3} [.1-3个数字]匹配3次，(?!.)最后不能有任何字符
            pattern = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}(?!.)')
            s = pattern.findall(client_server_ip)
            if s == []:
                self.msg_failed("IP地址非法")
                return

        if client_password == '':
            self.msg_failed("请填写密码")
            return

        if pingIP(client_server_ip) == 0 and pingIP(author_server.server_ip) == 0 :
            try:
                #清理一下服务器的ssh主机记录的指纹配置，以防待授权服务器的IP地址被多次使用
                logging.debug("-----清理主机指纹-----")
                cmd = 'echo > ~/.ssh/known_hosts'
                ssh(author_server.server_ip,
                    22,
                    author_server.server_username,
                    author_server.server_password,
                    cmd)
                logging.debug("-----清理主机指纹完毕-----")

                #判断授权服务端是否存在存储池
                logging.debug("*****获取待授权服务端存储池信息*****")
                cmd = r"sshpass -p '{}' ssh -n -o StrictHostKeyChecking=no {}@{} osnpool list".format(client_password,
                                                                                                      client_username,
                                                                                                      client_server_ip)
                logging.debug(cmd)
                output,flag = ssh(author_server.server_ip,
                                  22,
                                  author_server.server_username,
                                  author_server.server_password,
                                  cmd)
                logging.debug(output)
                if output != '':
                    self.msg_failed("待授权服务器存在存储池，无法安装测试授权")
                    return
                logging.debug("*****获取待授权服务端存储池信息完毕*****")

                #用授权服务器从待授权服务器上获取UUID
                logging.debug("*****获取UUID*****")
                cmd = r"sshpass -p '{}' ssh -n -o StrictHostKeyChecking=no {}@{} osn_license_util -D".format(client_password,
                                                                                                               client_username,
                                                                                                               client_server_ip)
                logging.debug(cmd)
                output,flag = ssh(author_server.server_ip,
                             22,
                             author_server.server_username,
                             author_server.server_password,
                             cmd)
                logging.debug(output)
                pattern = re.compile(r'[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}')
                client_uuid = pattern.findall(str(output))[0]
                logging.debug("*****获取UUID完毕*****")

                #在授权服务器上制作测试授权
                logging.debug("-----制作授权-----")
                cmd = r'osn_license_util -N -u {} -f -i -d -r -v -m -c 12 ' \
                      r'-p $((1024*1024)) -k {} -o {}/{}.lic -t -e 60'.format(client_uuid,
                                                                              author_server.private_key_path,
                                                                              author_server.lic_path,
                                                                              client_uuid)
                ssh(author_server.server_ip,
                    22,
                    author_server.server_username,
                    author_server.server_password,
                    cmd)
                logging.debug("-----授权制作完毕-----")

                # 从授权服务器上把授权拷贝到待授权服务器
                logging.debug("*****拷贝授权*****")
                cmd = r"sshpass -p '{}' scp {}/{}.lic {}@{}:/tmp/{}.lic".format(client_password,
                                                                              author_server.lic_path,
                                                                              client_uuid,
                                                                              client_username,
                                                                              client_server_ip,
                                                                              client_uuid)

                ssh(author_server.server_ip,
                    22,
                    author_server.server_username,
                    author_server.server_password,
                    cmd)
                logging.debug("*****拷贝授权完毕*****")

                #在待授权服务器上安装授权
                logging.debug(r'-----开始远程安装授权-----')
                logging.debug(client_uuid)
                cmd = r'osn_license_util -I -l /tmp/{}.lic'.format(client_uuid)
                logging.debug(cmd)
                logging.debug(client_server_ip)
                logging.debug(client_username)
                logging.debug(client_password)
                output,flag = ssh(client_server_ip,
                             22,
                             client_username,
                             client_password,
                             cmd)
                logging.debug(output)
                logging.debug(r'-----远程安装授权结束-----')
                if output != 'The new license is installed successfully\n':
                    self.msg_failed("安装失败，错误信息:{}".format(output))
                else:
                    logging.debug("*****启用iSCSI Target*****")
                    cmd = r"sshpass -p '{}' ssh -n -o StrictHostKeyChecking=no {}@{} osnsanmgr --lschn".format(client_password,
                                                                                                               client_username,
                                                                                                               client_server_ip)
                    logging.debug(cmd)
                    output,flag = ssh(author_server.server_ip,
                                 22,
                                 author_server.server_username,
                                 author_server.server_password,
                                 cmd)
                    output = output.split('\n') #按行分割字符串
                    logging.debug(output)
                    iqn = ''
                    state = ''
                    for line in output:
                        if line != '':
                            line = line.split() #按空格分割每一行
                            if line[2] == 'Virtual':
                                iqn = line[0]
                                state = line[5]
                    if iqn == '':
                        logging.debug('不存在iSCSI Target')
                    else:
                        if state != 'disabled': #判断iSCSI Target是否被禁用
                            logging.debug('iSCSI Target已经启用')
                        else:
                            cmd = 'osnsanmgr --enable -t {}'.format(iqn)
                            cmd = r"sshpass -p '{}' ssh -n -o StrictHostKeyChecking=no {}@{} {}".format(client_password,
                                                                                                        client_username,
                                                                                                        client_server_ip,
                                                                                                        cmd)
                            logging.debug(cmd)
                            output = ssh(author_server.server_ip,
                                         22,
                                         author_server.server_username,
                                         author_server.server_password,
                                         cmd)
                    logging.debug("*****iSCSI Target结束*****")

                    #记录信息
                    currentTime = datetime.datetime.now()
                    hostname = socket.gethostname()
                    ip = socket.gethostbyname(hostname)
                    user_name = 'user'
                    record = r'[{}][{}][{}][{}][{}][{}][{}]'.format(currentTime, hostname, ip, user_name, client_uuid, '测试版', '内部测试')
                    cmd = 'echo {} >> {}'.format(record, author_server.log_path)
                    ssh(author_server.server_ip,
                        22,
                        author_server.server_username,
                        author_server.server_password,
                        cmd)
                    logging.info('Streamer在线授权成功')
                    self.msg_success('在线授权成功')
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                self.msg_failed("端口错误，可能是服务器IP地址不对")
            except paramiko.ssh_exception.AuthenticationException as e:
                self.msg_failed("认证错误，可能是用户名密码错误")
            except Exception as e:
                logging.exception('未知错误')
                self.msg_failed("未知错误")
        else:
            self.msg_failed("授权服务器或待授权服务器离线")