# -*- coding: utf-8 -*-

' a caa workspace module '

__author__ = 'Luca Liu'

import os
import shutil
import re
from datetime import datetime
from caafinder.database import database

class workspace(object):
    def __init__(self, workspaceName):
        self.__backupPath = os.getcwd()
        workspacePath = os.path.join(os.getcwd(),workspaceName)
        if os.path.exists(workspacePath) and isWorkspace(workspacePath):
            self.__name = workspaceName
            self.parseWorkspace()
            self.__data = database()
            if len(self.__data) == 0:
                self.__data.initDatabase(os.getcwd())
        else:
            self.__name = None

    def parseWorkspace(self):
        self.__info = {}
        workspacePath = os.path.join(os.getcwd(),self.__name)
        listFrm = [x for x in os.listdir(workspacePath) \
                   if os.path.isdir(os.path.join(workspacePath,x)) \
                   and x != 'win_b64' and x != 'ToolsData']
        for eachFrm in listFrm:
            eachFrmPath = os.path.join(workspacePath,eachFrm)
            self.__info[eachFrmPath] = []
            listMod = [x for x in os.listdir(eachFrmPath) \
                       if os.path.isdir(os.path.join(eachFrmPath,x)) \
                       and x.find('.m') > 0]
            for eachMod in listMod:
                eachModPath = os.path.join(eachFrmPath,eachMod)
                self.__info[eachFrmPath].append(eachModPath)

    def backup(self):
        if self.__name != None:
            workspacePath = os.path.join(os.getcwd(),self.__name)
            backupName = self.__name + "_" + datetime.now().strftime('%m%d_%H%M')
            targetPath = os.path.join(self.__backupPath,backupName)
            os.mkdir(targetPath)

            copiedPathList = [x for x in os.listdir(workspacePath) if os.path.isdir(os.path.join(workspacePath, x)) and x != 'win_b64' and x != 'ToolsData' and x != '.git']
            for each in copiedPathList:
                copiedPath = os.path.join(workspacePath, each)
                copytoPath = os.path.join(targetPath, each)
                shutil.copytree(copiedPath, copytoPath)
                ObjectsToDelete = []
                for x in os.walk(copytoPath):
                    if os.path.split(x[0])[1] == 'win_b64':
                        ObjectsToDelete.append(x[0])
                for x in ObjectsToDelete:
                    shutil.rmtree(x)
                print ("copy " + each + " to " + targetPath + " success")

    def complete(self,moduel = 'all'):
        moduelPath = []
        if self.__name != None:
            for x in self.__info:
                for y in self.__info[x]:
                    if os.path.split(y)[1] == moduel or moduel == 'all':
                        moduelPath.append(os.path.join(y,'src'))
            cppList = []
            for each in moduelPath:
                for x in [x for x in os.listdir(each) if os.path.isfile(os.path.join(each,x)) and x.split('.')[1] == 'cpp']:
                    cppList.append(os.path.join(each,x))

            print(cppList[0])
            print(parseCpp(cppList[0]))



    @property
    def name(self):
        return self.__name
    @property
    def info(self):
        print(self.__name)
        if self.__name != None:
            for x in self.__info:
                print('\t',os.path.split(x)[1])
                for y in self.__info[x]:
                    print('\t\t',os.path.split(y)[1])

    @property
    def backupPath(self):
        return self.__backupPath
    @backupPath.setter
    def backupPath(self,value):
        if os.path.exists(value):
            self.__backupPath = value
        else:
            print("backupPath set wrong")

    @property
    def database(self):
        if self.__name != None:
            return self.__data
        else:
            return None




# 判定路径为workspace
def isWorkspace(path):
    listDir = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path,x))]
    if 'win_b64' in listDir and 'ToolsData' in listDir :
        return True
    else:
        try:
            listDir.remove('win_b64')
        except ValueError :
            print('no win_b64 in workspace')
        try:
            listDir.remove('ToolsData')
        except ValueError :
            print('no ToolsData in workspace')
        flag = False
        for each in listDir:
            childPath = os.path.join(path,each)
            if 'IdentityCard' in os.listdir(childPath):
                flag = True
            else:
                flag = False
        return flag


# 解析获取cpp所用的变量或类型
def parseCpp(cppPath):
    result = set()
    f = open(cppPath, 'r',encoding='iso-8859-1')
    content = f.read()
    f.close()

    for each in re.findall('CATLIST(.*?)\)',content,re.S):
        result.add('CATLIST'+each+')')
    for each in re.findall('/\*(.*?)\*/',content,re.S):
        content = content.replace(each,' ')
    for each in ('!','\"',';','->','}','{','(',')',':',"*",',','.','_','/','\t','\n','\\','+','&','=','<','>','%','|','-','[',']'):
        content = content.replace(each, ' ')
    for each in re.findall(' (.*?) ',content,re.S):
        result.add(each)
    return result

# 解析头文件
def parseHeader(headerPath):
    result = []
    if os.path.isfile(headerPath) and os.path.splitext(headerPath)[1] == '.h' :
        f = open(headerPath, 'r')
        for line in f.readlines():
            index = line.strip().find('#include')
            if index >= 0 and line[0] != '/':
                result.append(line.strip()[8:].replace('<','').replace('\"','').replace(' ',''))
        f.close()
    return result

# 解析Imakefile
def parseImakefile(imakefilePath):
    result = 'NoFinded'
    if os.path.isfile(imakefilePath) and os.path.split(imakefilePath)[1] == 'Imakefile.mk' :
        f = open(imakefilePath, 'r')
        for line in f.readlines():
            if line.strip().find('BUILT_OBJECT_TYPE') >= 0:
                result = line.strip()[line.find('=')+1:]
        f.close()
    return result

# 解析workspace
def parseWorkspace(workSpacePath):
    result = {}
    res = []
    os.path.walk(workSpacePath,visitForParseWS,res)
    for each in res:
        for x in os.listdir(os.path.join(each,'src')):
            temp = os.path.join(os.path.join(each,'src'),x)
            if os.path.splitext(temp)[1] == '.cpp':
                cpp = os.path.split(temp)[1]
                headerList = [cpp.split('.')[0] + '.h','NoFinded']
                os.path.walk(each,visitForFindHeader,headerList)
                imakefile = os.path.join(each,'Imakefile.mk')
                identityCard = os.path.join(os.path.join(os.path.split(each)[0],'IdentityCard'),'IdentityCard.xml')
                result[cpp] = [imakefile,identityCard,headerList[1]]
    return result


def visitForFindHeader(arg, dirname, names):
    for each in names:
        if arg[0] == each:
            arg[1] = os.path.join(dirname,each)

# 寻找moduel的visit函数
def visitForParseWS(arg, dirname, names):
    moduelNameSplit = os.path.split(dirname)[1].split('.')
    upperPath = os.path.split(os.path.split(dirname)[0])[1]
    if len(moduelNameSplit) == 2 and moduelNameSplit[1] == 'm' and upperPath != 'win_b64':
        arg.append(dirname)
        for each in names:
            childPath = os.path.join(dirname, each)
            if(os.path.isfile(childPath)):
                ext = os.path.splitext(childPath)[1]
                if (ext == '.cpp') and (os.path.split(dirname)[1] == 'src'):
                    arg.append(childPath)





# 修改头文件
def modifyHeader(headerPath,cppPath):
    result = {}
    f = open(headerPath, 'r')
    content = f.read()
    f.close()
    header = set()

    headerList = re.findall('include(.*?)\n',content)
    for each in headerList:
        str = each.replace('"','').replace('>','').replace('<','').replace(' ','')
        if str.find('.') == -1:
            str = str + '.h'
        header.add(str)

    conn = sqlite3.connect(databasePath)
    cursor = conn.cursor()

    for each in parseCpp(cppPath):
        cursor.execute('select * from method where header=?', (each,))
        values = cursor.fetchmany(1)
        if len(values) >= 1:
            header.add(each)
    for each in header:
        cursor.execute('select * from method where header=?', (each,))
        values = cursor.fetchmany(1)
        framework = "Custome"
        if len(values) >= 1:
            framework = values[0][4]
        elif each[0].islower():
            framework = "Standard C++ Libary"
        if framework in result:
            result[framework].append(each)
        else:
            result[framework] = [each]

    cursor.close()
    conn.commit()
    conn.close()

    deleteArea = "#include" + headerList[0] + re.findall('%s(.*?)%s'%(headerList[0],headerList[-1]),content,re.S)[0] + headerList[-1]
    # print deleteArea
    updateArea = "//-------------------------------\n// add the DS Header by CAAFinder\n//-------------------------------\n\n"

    for key in result.keys():
        updateArea += "// %s\n"%key
        for value in result[key]:
            updateArea += '#include "%s"\n'%value
        updateArea += "\n"
    # print updateArea
    content = content.replace(deleteArea,updateArea)

    # print content
    f = open(headerPath, 'w')
    f.write(content)
    f.close()


# 修改imakefile文件
# def modifyImakeFile(imakeFilePath, headerPath):
#     result = {}
#     f = open(imakeFilePath, 'r')
#     content = f.read()
#     f.close()
#     moduel = set()
#
#     deleteArea = re.findall('WIZARD_LINK_MODULES =(.*?)END WIZARD EDITION ZONE',content,re.S)[0]
#     temp = deleteArea
#     for each in ['\\','\n','\t','#']:
#         temp = temp.replace(each,' ')
#     for each in temp.split(' '):
#         if len(each) > 0:
#             moduel.add(each)
#     f = open(headerPath,'r')
#     content = f.read()
#     f.close()
#
#
#     conn = sqlite3.connect(databasePath)
#     cursor = conn.cursor()
#
#     for each in re.findall('#include "(.*?)"',content):
#         cursor.execute('select * from method where header=?', (each,))
#         values = cursor.fetchmany(1)
#         if len(values) >= 1:
#             moduel.add(values[0][3])
#
#     cursor.close()
#     conn.commit()
#     conn.close()
#     updateArea = "\\\n"
#     for each in moduel:
#         updateArea += (each + ' \\\n')
#     updateArea += "#"
#
#     print deleteArea
#     print content.find(deleteArea)










if __name__=='__main__':
    # iniDatabase('/Users/guti/Developer/CAAFinderffffff/Resource/generated')
    print(os.getcwd())
    a = workspace('GW_GWS_LC')
    a.info
    print(len(a.database))
