# -*- coding:utf-8 -*-
import threading
import logging

logger = logging.getLogger('root.ComputerPowerControlTool.ComputerPowerControlToolThreads')

from InfoCoreTools.PsExc64 import windowsRebootRemoteMachine
from InfoCoreTools.SSH import linuxRebootRemoteMachine
from InfoCoreTools.vSphereCLI import startVirtualMachineHard
from InfoCoreTools.vSphereCLI import stopVirtualMachineHard
from InfoCoreTools.WindowsCMD import pingIP
from InfoCoreTools.IPMI import powerOn
from InfoCoreTools.IPMI import powerOff

class PowerOnThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, server, thread_name=None, parent=None):
        super(PowerOnThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.server = server

    def run(self):
        computer_type = self.server.computer_type
        os_type = self.server.os_type
        ip_address = self.server.ip_address
        username = self.server.username
        password = self.server.password
        is_ipmi_enabled = self.server.is_ipmi_enabled
        ipmi_ip = self.server.ipmi_ip
        ipmi_username = self.server.ipmi_username
        ipmi_password = self.server.ipmi_password
        is_vm = self.server.is_vm
        vm_name = self.server.vm_name
        esxi_ip = self.server.esxi_ip
        esxi_username = self.server.esxi_username
        esxi_password = self.server.esxi_password

        logging.info("---打开电源线程开始---")
        if computer_type == '实体机':
            logging.info("检测到{}为：实体机".format(ip_address))
            if is_ipmi_enabled:
                logging.info("{}已经配置IPMI信息".format(ip_address))
                powerOn(ipmi_ip,ipmi_username,ipmi_password)
            else:
                logging.error("为配置IPMI信息，无法打开实体机{}的电源".format(ip_address))
        else:
            logging.info("检测到{}为：虚拟机".format(ip_address))
            if is_vm:
                logging.info("{}已经配置虚拟机主机信息".format(ip_address))
                startVirtualMachineHard(esxi_ip, esxi_username, esxi_password, vm_name)
            else:
                logging.error("未配置虚拟机主机信息，无法打开虚拟机{}的电源".format(ip_address))
        logging.info("---打开电源线程结束---")

class PowerOffThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, server, thread_name=None, parent=None):
        super(PowerOffThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.server = server

    def run(self):
        computer_type = self.server.computer_type
        os_type = self.server.os_type
        ip_address = self.server.ip_address
        username = self.server.username
        password = self.server.password
        is_ipmi_enabled = self.server.is_ipmi_enabled
        ipmi_ip = self.server.ipmi_ip
        ipmi_username = self.server.ipmi_username
        ipmi_password = self.server.ipmi_password
        is_vm = self.server.is_vm
        vm_name = self.server.vm_name
        esxi_ip = self.server.esxi_ip
        esxi_username = self.server.esxi_username
        esxi_password = self.server.esxi_password

        logging.info("---关闭电源线程开始---")
        if computer_type == '实体机':
            logging.info("检测到{}为：实体机".format(ip_address))
            if is_ipmi_enabled:
                logging.info("{}已经配置IPMI信息".format(ip_address))
                powerOff(ipmi_ip,ipmi_username,ipmi_password)
            else:
                logging.error("为配置IPMI信息，无法打开实体机{}的电源".format(ip_address))
        else:
            logging.info("检测到{}为：虚拟机".format(ip_address))
            if is_vm:
                logging.info("{}已经配置虚拟机主机信息".format(ip_address))
                stopVirtualMachineHard(esxi_ip, esxi_username, esxi_password, vm_name)
            else:
                logging.error("未配置虚拟机主机信息，无法打开虚拟机{}的电源".format(ip_address))
        logging.info("---关闭电源线程结束---")

class RebootThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。
    def __init__(self, server,thread_name=None, parent=None):
        super(RebootThread, self).__init__(parent)
        self.thread_name = thread_name  # 将传递过来的name构造到类中的name
        self.server = server

    def run(self):
        computer_type = self.server.computer_type
        os_type = self.server.os_type
        ip_address = self.server.ip_address
        username = self.server.username
        password = self.server.password
        is_ipmi_enabled = self.server.is_ipmi_enabled
        ipmi_ip = self.server.ipmi_ip
        ipmi_username = self.server.ipmi_username
        ipmi_password = self.server.ipmi_password
        is_vm = self.server.is_vm
        vm_name = self.server.vm_name
        esxi_ip = self.server.esxi_ip
        esxi_username = self.server.esxi_username
        esxi_password = self.server.esxi_password

        logging.info("---重启服务器线程开始---")
        if os_type == 'Windows':
            logging.info("检测到{}是Windows".format(ip_address))
            if pingIP(ip_address) == 0:
                windowsRebootRemoteMachine(ip_address, username, password)
            else:
                logging.error("{}无法ping通".format(ip_address))
        else:
            logging.info("检测到{}是Linux".format(ip_address))
            if pingIP(ip_address) == 0:
                linuxRebootRemoteMachine(ip_address,username,password)
            else:
                logging.error("{}无法ping通".format(ip_address))
        logging.info("---重启服务器线程结束---")