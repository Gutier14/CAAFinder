# -*- coding: utf-8 -*-

from caafinder.workspace import workspace
from caafinder.database import database
import os

if __name__=='__main__':
    print(os.getcwd())
    ws = workspace('WS')
    data = ws.data
    print(len(data))