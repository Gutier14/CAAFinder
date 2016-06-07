# -*- coding: utf-8 -*-

from caafinder.workspace import workspace
from caafinder.database import database
import os

print('hello')

# if __name__=='__main__':
#     name = input('请输入需要管理的workspace名字:')
#     ws = workspace(name)
#     ws.info
#     flag = input("workspace解析正确?yes or no:")
#     if flag == 'yes' or flag == 'y':
#         if len(ws.database) == 0:
#             caadoc = input("需要初始化数据库,请输入caadoc的路径:")
#             ws.database.initDatabase(caadoc)
#         backup = input("需要备份?yes or no:")
#         if backup == 'yes' or backup == 'y':
#             ws.backup()
#         complete = input("需要自动补全?yes or no:")
#         if complete == 'yes' or backup == 'y':
#             ws.complete()
#             print("Game Over")
#     if flag == 'auto':
#         if len(ws.database) > 0:
#             ws.backup()
#             ws.complete()
