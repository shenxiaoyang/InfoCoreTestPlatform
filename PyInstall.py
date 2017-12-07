# -*- coding:utf-8 -*-
import os
import traceback

try:
      cmd1 = r'C:\Users\TEST001\AppData\Local\Programs\Python\Python35\Scripts\pyinstaller.exe' \
            r' -F  C:\Users\TEST001\PycharmProjects\InfoCoreTestPlatform\InfoCoreTestPlatform.py'
      os.system(cmd1)

      cmd2 = r'start C:\Users\TEST001\PycharmProjects\InfoCoreTestPlatform\dist\InfoCoreTestPlatform.exe'
      os.system(cmd2)
except BaseException:
      print(traceback.print_exc())