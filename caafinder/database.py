# -*- coding: utf-8 -*-

' a CAA sqlite3 database module '

__author__ = 'Luca Liu'

import os
import re
import sqlite3
import hashlib

# id , method ,fullname ,DStype , header , moduel , framework

class database(object):
    def __init__(self):
        self.__path = None
        for x in os.walk(os.getcwd()):
            for y in x[2]:
                if y == 'DSInterface.db':
                    self.__path = os.path.join(x[0],y)
                    break
        if self.__path == None:
            self.__path = os.path.join(os.getcwd(),'DSInterface.db')
            conn = sqlite3.connect(self.__path)
            cursor = conn.cursor()
            cursor.execute('create table interface (id varchar(40) primary key, method varchar(40),fullname varchar(200),DStype varchar(20), header varchar(20), moduel varchar(20), framework varchar(20))')
            cursor.close()
            conn.commit()
            conn.close()

    def insert(self,type,framework,header = 'None',moduel = 'None',method = 'None',fullname = 'None'):
        if header == 'None':
            header = type + '.h'
        md5obj=hashlib.md5()
        md5obj.update((method+fullname+type+header+moduel+framework).encode('utf-8'))
        id = md5obj.hexdigest()

        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute("select id from interface WHERE id = '%s' " % id)
        if len(cursor.fetchall()) > 0:
            print('the item has inserted')
        else:
            print(id,method,fullname,type,header,moduel,framework)
            cursor.execute("insert into interface (id, method, fullname, DStype, header, moduel, framework) values ('%s','%s','%s', '%s', '%s', '%s', '%s')" % (id,method,fullname,type,header,moduel,framework))
            print('insert:',method,fullname,header,moduel,framework)
        cursor.close()
        conn.commit()
        conn.close()

    def initDatabase(self,caaDocPath):
        if os.path.exists(caaDocPath):
            MasterIdx = ""
            for each in os.walk(caaDocPath):
                if 'MasterIdx.htm' in each[2]:
                    MasterIdx = os.path.join(each[0],'MasterIdx.htm')
                    break
            urlset = set()
            if MasterIdx != '':
                f = open(MasterIdx,'r',encoding='iso-8859-1')
                content = f.read()
                f.close()
                basePath = MasterIdx.split('/_index')[0]
                for each in re.findall('<a href="(.*?)"',content,re.S):
                    if '#' in each:
                        each = each.split('#')[0]
                    each = basePath + each[2:]
                    if os.path.isfile(each):
                        urlset.add(each)
            print(len(urlset),'pages need to parse')
            for each in urlset:
                self.parsePage(each)

    def parsePage(self,path):
        if os.path.exists(path):
            f = open(path,'r',encoding='iso-8859-1')
            page = f.read()
            f.close()
            titleList = re.findall('<title>(.*?)</title>',page,re.S)
            moduelList = re.findall('include the module: <b>(.*?)</b>',page,re.S)
            headerList = re.findall('included in the file: <b>(.*?)</b>',page,re.S)
            methodList = re.findall('<a href="#(.*?)">',page,re.S)
            if len(titleList) >= 1 and len(headerList) >= 1:
                framework = titleList[0].split(' ')[0]
                type = titleList[0].split(' ')[-1]
                header = headerList[0]
                moduel = 'None'
                method = 'None'
                fullname = 'None'
                if len(moduelList) >= 1:
                    moduel = moduelList[0]
                if len(methodList) >= 1:
                    for x in methodList:
                        fullname = x
                        method = x.split('(')[0]
                        md5obj=hashlib.md5()
                        md5obj.update((method+fullname+type+header+moduel+framework).encode('utf-8'))
                        id = md5obj.hexdigest()
                        self.insert(type,framework,header,moduel,method,fullname)
                else:
                    md5obj=hashlib.md5()
                    md5obj.update((method+fullname+type+header+moduel+framework).encode('utf-8'))
                    id = md5obj.hexdigest()
                    self.insert(type,framework,header,moduel,method,fullname)


                print('parse ', os.path.split(path)[1], ' successful')
            else:
                print("parse Wrong:",path)
        else:
            print("file don't exist:", path)

    def querryByHeader(self,header):
        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute("select * from interface WHERE header = '%s' " % header)
        result = cursor.fetchmany(1)
        if len(result) == 1:
            return (result[0][-2],result[0][-1])
        else:
            return None

    def querryByType(self, type):
        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute("select * from interface WHERE DStype = '%s' " % type)
        result = cursor.fetchmany(1)
        if len(result) == 1:
            return (result[0][-3],result[0][-2],result[0][-1])
        else:
            return None

    def querryByModuel(self,moduel):
        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute("select * from interface WHERE moduel = '%s' " % moduel)
        result = cursor.fetchmany(1)
        if len(result) == 1:
            return result[0][-1]
        else:
            return None
    def querryByFramework(self,framework):
        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute("select * from interface WHERE framework = '%s' " % framework)
        result = cursor.fetchmany(1)
        if len(result) == 1:
            return True
        else:
            return None


    def __len__(self):
        conn = sqlite3.connect(self.__path)
        cursor = conn.cursor()
        cursor.execute('select id from interface')
        num = len(cursor.fetchall())
        cursor.close()
        conn.commit()
        conn.close()
        return num

if __name__=='__main__':
    db = database()
    # db.initDatabase('/Users/guti/Developer/CAAFinderffffff')
    print(len(db))
    print(db.querryByHeader('CATBoolean.h'))
    # print(db.querryByType('CATDlgUtility'))
    # print(db.querryByModuel('JS0FM'))
