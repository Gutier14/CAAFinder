# -*- coding: utf-8 -*-

' a caa workspace module '

__author__ = 'Luca Liu'

import os
import shutil
import re
import sqlite3
from datetime import datetime
from caafinder.database import database
from lxml import etree


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
        moduelRes = {}
        frameworkRes = {}
        moduelPath = []
        if self.__name != None:
            for x in self.__info:
                for y in self.__info[x]:
                    if os.path.split(y)[1] == moduel or moduel == 'all':
                        moduelPath.append(os.path.join(y,'src'))
            cppList = []
            for each in moduelPath:
                for x in [x for x in os.listdir(each) if os.path.isfile(os.path.join(each,x)) and x.split('.')[1] == 'cpp']:
                    cppPath = os.path.join(each,x)
                    res = {}
                    print(cppPath)
                    for y in parseCpp(cppPath):
                        temp = self.__data.querryByType(y)
                        if temp != None:
                            res[temp[0]] = (temp[1],temp[2])
                    FRPath = ''
                    for y in self.__info:
                        if os.path.split(each)[0] in self.__info[y]:
                            FRPath = y
                            break
                    headerPath = ''
                    for y in os.walk(FRPath):
                        if x.replace('cpp','h') in y[2]:
                            temp = os.path.join(y[0],x.replace('cpp','h'))
                            f = open(temp,'r',encoding='iso-8859-1')
                            cont = f.read()
                            f.close()
                            if '#include' in cont:
                                headerPath = temp
                                break

                    for y in parseHeader(headerPath):
                        if y in res:
                            pass
                        elif self.__data.querryByHeader(y) != None:
                            res[y] = self.__data.querryByHeader(y)
                        else:
                            res[y] = ('None','Custom')
                    self.__modifyHeader(headerPath, res)
                    print(headerPath)
                    Moduel = os.path.split(each)[0]
                    print(Moduel)
                    print(FRPath)
                    for y in res:
                        if Moduel in moduelRes:
                            moduelRes[Moduel].add(res[y][0])
                        else:
                            moduelRes[Moduel] = set()
                            moduelRes[Moduel].add(res[y][0])
                        if FRPath in frameworkRes:
                            frameworkRes[FRPath].add(res[y][1])
                        else:
                            frameworkRes[FRPath] = set()
                            frameworkRes[FRPath].add(res[y][1])

        mkPathList = map(lambda x:x.replace('src','Imakefile.mk'),moduelPath)

        for each in mkPathList:
            moduelSet = moduelRes[os.path.split(each)[0]]
            for x in self.parseImakefile(each):
                moduelSet.add(x)
            if 'None' in moduelSet:
                moduelSet.remove('None')
            self.__modifyImakefile(each,moduelSet)

        for each in frameworkRes:
            identitycardPath = os.path.join(os.path.join(each,'IdentityCard'),'IdentityCard.xml')
            self.__modifyIdentityCard(identitycardPath,frameworkRes[each])

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


    def __modifyHeader(self,headerPath, res):

        f = open(headerPath, 'r',encoding='iso-8859-1')
        content = f.read()
        f.close()

        headerList = re.findall('include(.*?)\n',content)
        deleteArea = "#include" + headerList[0] + re.findall('%s(.*?)%s'%(headerList[0],headerList[-1]),content,re.S)[0] + headerList[-1]
        # print(deleteArea)

        updateArea = "//-------------------------------\n// add the DS Header by CAAFinder\n//-------------------------------\n\n"

        result = {}
        for each in res:
            if res[each][1] in result:
                result[res[each][1]].append(each)
            else:
                result[res[each][1]] = [each]
        for each in result:
            updateArea += ('// ' + each + '\n')
            for eachHeader in result[each]:
                if eachHeader.find('>') >= 0:
                    updateArea += ("#include " + eachHeader + '\n')
                else:
                    updateArea += ("#include \"" + eachHeader + "\"" + '\n')

        content = content.replace(deleteArea,updateArea)
        f = open(headerPath, 'w',encoding='iso-8859-1')
        f.write(content)
        f.close()

    def parseImakefile(self,imakefilePath):
        result = {}
        if os.path.isfile(imakefilePath) and os.path.split(imakefilePath)[1] == 'Imakefile.mk' :
            f = open(imakefilePath, 'r',encoding='iso-8859-1')
            for line in f.readlines():
                if line[0] == '#' or line[0] == '/':
                    pass
                else:
                    selector = [x for x in line.replace('\\',' ').replace('=',' ').split(' ') if len(x) > 3]
                    for each in selector:
                        fr = self.__data.querryByModuel(each)
                        if fr != None:
                            result[each] = fr
            f.close()
        return result

    def __modifyImakefile(self,imakefile,res):
        moduel = os.path.split(os.path.split(imakefile)[0])[1].split('.')[0]
        content = '#======================================================================\n'
        content += '# Imakefile for module %s\n' %moduel
        content += '#======================================================================\n'
        content += '#  %s Creation: Code generated by the CaaFinder\n'%datetime.now().strftime('20%y-%m-%d')
        content += '#======================================================================\n'
        content += '\n\n'
        content += 'BUILT_OBJECT_TYPE=SHARED LIBRARY\n#BUILT_OBJECT_TYPE=LOAD MODULE\n'
        content += '\n\n'
        content += 'LINK_WITH = \\\n'
        for each in res:
            content += '%s \\\n'%each
        content += '\n\n'
        content += '#https://github.com/Gutier14/CAAFinder\n'
        content += '#email: geekluca@qq.com\n'

        f = open(imakefile,'w',encoding='iso-8859-1')
        f.write(content)
        f.close()
        print(imakefile)

    def __modifyIdentityCard(self,identitycardPath,res):
        print(identitycardPath)
        f = open(identitycardPath,'r',encoding='iso-8859-1')
        conent = f.read()
        f.close()

        identityCard = etree.XML(conent.encode('utf-8'))

        container = set()

        for each in identityCard:
            apptr = each.attrib
            container.add(apptr['name'])

        # print(len(container))
        for each in res:
            if each in container:
                pass
            else:
                child = etree.Element("prerequisite", name=each,access="Public")
                identityCard.append(child)
        # print(len(identityCard))
        f = open(identitycardPath,'w',encoding='iso-8859-1')
        f.write(etree.tostring(identityCard, xml_declaration=True).decode('iso-8859-1'))
        f.close()




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
        if each[0] == 'V':
            result.add('CATListVal'+each[2:])
        elif each[0] == 'P':
            result.add('CATListPtr'+each[2:])
            result.add('CATListOf'+each[2:])

    for each in re.findall('/\*(.*?)\*/',content,re.S):
        content = content.replace(each,' ')
    for each in ('!','\"',';','->','}','{','(',')',':',"*",',','.','_','/','\t','\n','\\','+','&','=','<','>','%','|','-','[',']'):
        content = content.replace(each, ' ')
    for each in re.findall(' (.*?) ',content,re.S):
        if len(each) > 4 and each[:3] == 'CAT':
            result.add(each)
    return result

# 解析头文件
def parseHeader(headerPath):
    result = []
    if os.path.isfile(headerPath) and os.path.splitext(headerPath)[1] == '.h' :
        f = open(headerPath, 'r',encoding='iso-8859-1')
        for line in f.readlines():
            index = line.strip().find('#include')
            if index >= 0 and line[0] != '/':
                result.append(line.strip()[8:].replace('\"','').replace(' ',''))
        f.close()
    return result










if __name__=='__main__':
    a = workspace('GW_WS_LC')
    a.complete()
    # a.complete('GWSDDPartProofreader.m')
    # parseIdentityCard('/Users/guti/Developer/CAAFinder/caafinder/GW_GWS_LC/GWStruct/IdentityCard/IdentityCard.xml')
