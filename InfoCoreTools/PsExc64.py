# -*- coding: utf-8 -*-

#PsExec是一个轻型的 telnet 替代工具，它使您无需手动安装客户端软件即可执行其他系统上的进程，并且可以获得与控制台应用程序相当的完全交互性。
#PsExec最强大的功能之一是在远程系统和远程支持工具中启动交互式命令提示窗口，以便显示无法通过其他方式显示的有关远程系统的信息。
#注意这个exe在调用前，先用cmd命令行打开运行打开一下，它会有一个询问对话框，需要第一次确认一下。

import sys
import logging
import os

logger = logging.getLogger('root.InfoCoreTools.Psexc64')
psexec64 = r'{}\InfoCoreTools\PStools\PsExec64.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))
if not os.path.exists(psexec64):
    psexec64 = r'{}\PStools\PsExec64.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))
psexec32 = r'{}\InfoCoreTools\PStools\PsExec.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))
if not os.path.exists(psexec32):
    psexec32 = r'{}\PStools\PsExec.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))
bang = r'C:\Users\Administrator\Desktop\OSNAutoTest\osrbang.exe'
runDisktestBat = r'C:\Users\Administrator\Desktop\OSNAutoTest\RunDiskTest.bat'
startDebugviewBat = r'C:\Users\Administrator\Desktop\OSNAutoTest\StartDbgview.bat'
ench_on = True

#远程重启，用PsExec64.exe远程调用系统本地CMD命令（shutdown -r -t 0）实现
def rebootRemoteMachine(ip, username, password):
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c shutdown -r -t 0 2>nul".format(psexec64,ip,username,password)
    os.popen(cmd)

#远程正常关机，用PsExec64.exe远程调用系统本地CMD命令（shutdown -s -t 0）实现
def shutdownRemoteMachine(ip, username, password):
    logging.info('{}远程正常关机'.format(ip))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c shutdown -s -t 0 2>nul".format(psexec64,ip,username,password)
    os.popen(cmd)

def bangRemoteMachine(ip, username, password):
    logging.info('{} bang'.format(ip))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} {} -s >nul 2>nul".format(psexec64,ip,username,password,bang)
    os.popen(cmd)

def enableRemoteNetworkAdapter(ip, username, password, adapterName):
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c netsh interface set interface ""{}"" enabled 2>nul".format(psexec64,
                                                                                                         ip,
                                                                                                         username,
                                                                                                         password,
                                                                                                         adapterName)
    os.popen(cmd)

def disableRemoteNetworkAdapter(ip, username, password, adapterName):
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c netsh interface set interface ""{}"" disabled 2>nul".format(psexec64,
                                                                                                          ip,
                                                                                                          username,
                                                                                                          password,
                                                                                                          adapterName)
    os.popen(cmd)

def startRemoteMachineService(ip, username, password, serviceName):
    logging.debug('启动{}的{}服务'.format(ip,serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc start ""{}"" 2>nul".format(psexec64,
                                                                            ip,
                                                                            username,
                                                                            password,
                                                                            serviceName)
    os.popen(cmd)

def stopRemoteMachineService(ip, username, password, serviceName):
    logging.debug('停止{}的{}服务'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc stop ""{}"" 2>nul".format(psexec64,
                                                                           ip,
                                                                           username,
                                                                           password,
                                                                           serviceName)
    os.popen(cmd)

def chkconfigRemoteMachineServiceOn(ip, username, password, serviceName):
    logging.debug('设置{}的{}服务为开机自动启动'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc config ""{}"" start=auto 2>nul".format(psexec64,
                                                                                        ip,
                                                                                        username,
                                                                                        password,
                                                                                        serviceName)
    os.popen(cmd)

def chkconfigRemoteMachineServiceOff(ip, username, password, serviceName):
    logging.debug('设置{}的{}服务为开机手动启动'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc config ""{}"" start=demand 2>nul".format(psexec64,
                                                                                          ip,
                                                                                          username,
                                                                                          password,
                                                                                          serviceName)
    os.popen(cmd)

def queryRemoteService(ip, username, password, serviceName):
    logging.debug('查询{}的{}的状态'.format(ip,serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    state = 'UNKNOW'
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c sc queryex ""{}"" 2>nul" .format(psexec64,
                                                                            ip,
                                                                            username,
                                                                            password,
                                                                            serviceName)
    result = os.popen(cmd)
    output = result.read().split('\n')
    for line in output:
        line = line.split()
        if len(line)!=0 and line[0] == 'STATE' and line[3] == 'RUNNING':
            return 'RUNNING'
        if len(line)!=0 and line[0] == 'STATE' and line[3] == 'STOPPED':
            return 'STOPPED'
    return state

def runRemoteMachineDisktest(ip, username, password):
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c start {} 2>nul".format(psexec64,ip,username,password,runDisktestBat)
    os.popen(cmd)

def runRemoteMachineDebugview(ip, username, password):
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c start {} 2>nul".format(psexec64, ip, username, password,startDebugviewBat)
    os.popen(cmd)

def deleteRemoteMachineSystemDump(ip, username, password):
    dumpFile = r'C:\Windows\MEMORY.DMP'.replace(r'C:', r'\\{}\c$'.format(ip))
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c del {} 2>nul".format(psexec64, ip, username, password, dumpFile)
    os.popen(cmd)

def windows_do_cmd(ip, username, password, cmd):
    try:
        cmd1 = r'{} -s \\{} -u {} -p "{}" cmd.exe /c "{}" 2>&1'.format(psexec64,ip,username,password,cmd)
        logging.debug(cmd1)
        output = os.popen(cmd1)
        output1 = output.read().split('\n')[5]
        if output1.find("版本不兼容") != -1:
            logging.info('Psexec 64位版本获取失败，尝试使用32位版本')
            cmd2 = r'{} -s \\{} -u {} -p "{}" cmd.exe /c "{}" 2>&1'.format(psexec32, ip, username, password, cmd)
            logging.debug(cmd2)
            output = os.popen(cmd2)
            output1 = output.read().split('\n')[5]
        logging.debug(output1)
        return output1
    except BaseException:
        logging.exception('未知错误')