# -*- coding:utf-8 -*-
class AuthorServer():
    def __init__(self):
        self.server_ip = '192.168.11.173'
        self.server_username = 'root'
        self.server_password = 'okidoki'
        self.server_version_path = r'/Streamer_auth/config/version'
        self.server_version = ''
        self.private_key_path = r'/Streamer_auth/privkey.pem'
        self.login_info = r'/Streamer_auth/config/login'
        self.lic_path = r'/Streamer_auth/lic'
        self.log_path = r'/Streamer_auth/log/record.log'
        self.tmp_path = r'/Streamer_auth/tmp'
        self.is_online = False
        self.server_state = 0   #0表示未知，1表示在线，2表示连接错误，3表示版本不匹配

global author_server
author_server = AuthorServer()

#global ping_interval
#ping_interval = 5

#global monitor_ui_thread_event
#monitor_ui_thread_event = threading.Event()

#global client_version

#global run_path
#global is_log_enabled
#global user_permission
#global user_name

#user_name = ''
#user_permission = 0

#client_version = '1.5'