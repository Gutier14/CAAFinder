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

    def completeUnit(self,cppPath):
        data = self.__data

        mPath = os.path.join(os.path.split(os.path.split(cppPath)[0])[0],'Imakefile.mk')
        Fr = os.path.split(os.path.split(mPath)[0])[0]
        iPath = os.path.join(os.path.join(Fr,'IdentityCard'),'IdentityCard.xml')
        hPath = None
        for each in os.walk(Fr):
            for eachfile in each[2]:
                if eachfile == os.path.split(cppPath)[1].replace('cpp','h'):
                    tempPath = os.path.join(each[0],eachfile)
                    if os.path.exists(tempPath):
                        f = open(tempPath,'r',encoding='iso-8859-1')
                        content = f.read()
                        f.close()
                        if content.find(('class ' + eachfile.split('.')[0])) > 0 :
                            hPath = tempPath
                            break
        if hPath == None:
            return
        if os.path.exists(mPath) and os.path.exists(iPath) and os.path.exists(cppPath):
            DSType = parseCpp(cppPath,data)
            headerTuple = parseHeader(hPath,data)
            headerDS = headerTuple[0]
            headerCS = headerTuple[1]
            moduleTuple = parseImakefile(mPath,data)
            moduleDS = moduleTuple[0]
            moduleCS = moduleTuple[1]
            frameworkTuple = parseIdentityCard(iPath,data)
            frameworkDS = frameworkTuple[0]
            frameworkCS = frameworkTuple[1]


            for dstype in DSType:
                # header moduel framework
                dbTupleForDSType = data.querryByType(dstype)
                header = dbTupleForDSType[0]
                moduel = dbTupleForDSType[1]
                framework = dbTupleForDSType[2]

                if header not in headerDS and header != 'None':
                    headerDS.add(header)
                    print("add Header:" + header + ' to ' + hPath)
                if moduel not in moduleDS and moduel != 'None':
                    moduleDS.add(moduel)
                    print("add moduel:" + moduel + ' to ' + mPath)
                if framework not in frameworkDS and framework != 'None':
                    frameworkDS.add(framework)
                    print("add framework:" +framework+ ' to ' + iPath)


            modifyHeader(hPath,headerDS,headerCS,data)
            modifyImakefile(mPath,moduleDS,moduleCS)
            modifyIdentityCard(iPath,frameworkDS,frameworkCS)

    def completeModuel(self,moduel):
        moduelPath = ''
        for eachFr in self.__info:
            for eachModuel in self.__info[eachFr]:
                if os.path.split(eachModuel)[1].split('.')[0] == moduel:
                    moduelPath = eachModuel
        if moduelPath == '':
            return

        for eachdir in os.listdir(os.path.join(moduelPath,'src')):
            if eachdir.find('.cpp') > 0:
                cpp = os.path.join(os.path.join(moduelPath,'src'),eachdir)
                if os.path.exists(cpp):
                    self.completeUnit(cpp)

    def completeFramework(self,framework):
        frameworkPath = ''
        for eachFr in self.__info:
            if os.path.split(eachFr)[1] == framework:
                frameworkPath = eachFr
        if frameworkPath == '':
            return
        for eachdir in os.listdir(frameworkPath):
            path = os.path.join(frameworkPath,eachdir)
            if os.path.isdir(path) and eachdir.find('.m') > 0:
                self.completeModuel(eachdir.split('.')[0])

    def completeAll(self):
        for each in self.info:
            self.completeFramework(os.path.split(each)[1])


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

# 解析获取cpp
def parseCpp(cppPath, data=database()):
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
    delType = set()
    for each in result:
        if data.querryByType(each) == None:
            delType.add(each)
    for each in delType:
        result.remove(each)
    return result

# 解析头文件
def parseHeader(headerPath,data = database()):
    res = set()
    cus = set()
    if os.path.isfile(headerPath) and os.path.splitext(headerPath)[1] == 'h' :
        f = open(headerPath, 'r',encoding='iso-8859-1')
        content = f.read()
        f.close()

        for each in re.findall('#include "(.*?)"',content,re.S):
            if data.querryByHeader(each) != None:
                res.add(each)
            else:
                cus.add(each)
        for each in re.findall('#include <(.*?)>',content,re.S):
            cus.add(each)

    return (res,cus)

# 解析Imakefile
def parseImakefile(imakefilePath,data = database()):
        res = set()
        cus = set()
        if os.path.isfile(imakefilePath) and os.path.split(imakefilePath)[1] == 'Imakefile.mk' :
            f = open(imakefilePath, 'r',encoding='iso-8859-1')
            for line in f.readlines():
                if line[0] == '#' or line[0] == '/':
                    pass
                elif line.find('LINK_WITH = $(CAAFINDER_LINK_MODULES)') != -1:
                    for each in line.replace('LINK_WITH = $(CAAFINDER_LINK_MODULES)',' ').replace('\n',' ').split(' '):
                        if len(each) > 2:
                            cus.add(each)
                else:
                    selector = [x for x in line.replace('\\',' ').replace('=',' ').split(' ') if len(x) > 3]
                    for each in selector:
                        fr = data.querryByModuel(each)
                        if fr != None:
                            res.add(each)
            f.close()
        return (res,cus)

# 解析identityCard
def parseIdentityCard(identitycardPath,data = database()):

        res = set()
        cus = set()

        f = open(identitycardPath,'r',encoding='iso-8859-1')
        conent = f.read()
        f.close()

        identityCard = etree.XML(conent.encode('utf-8'))

        for each in identityCard:
            apptr = each.attrib
            fr = apptr['name']
            if data.querryByFramework(fr):
                res.add(fr)
            else:
                cus.add(fr)

        return (res,cus)

# 修改头文件
def modifyHeader(headerPath,res,cus = set(),data = database()):

        f = open(headerPath, 'r',encoding='iso-8859-1')
        content = f.read()
        f.close()

        deleteArea = ''
        deleteArealist = re.findall('// Add the DS Header by CAAFINDER(.*?)// END CAAFINDER EDITION ZONE',content,re.S)

        if len(deleteArealist) == 1:
            deleteArea = '// Add the DS Header by CAAFINDER' + deleteArealist[0] + '// END CAAFINDER EDITION ZONE'
        else:
            headerList = re.findall('include(.*?)\n',content)
            deleteArea = "#include" + headerList[0] + re.findall('%s(.*?)%s'%(headerList[0],headerList[-1]),content,re.S)[0] + headerList[-1]


        updateArea = "// Add the DS Header by CAAFINDER\n"

        result = {}
        for each in res:
            fr = data.querryByHeader(each)[1]
            if fr in result:
                result[fr].append(each)
            else:
                result[fr] = [each]

        for each in result:
            updateArea += ('// ' + each + '\n')
            for eachHeader in result[each]:
                if eachHeader.find('>') >= 0:
                    updateArea += ("#include " + eachHeader + '\n')
                else:
                    updateArea += ("#include \"" + eachHeader + "\"" + '\n')
        if len(cus)>0:

            result = set()
            for each in cus:
                if each.find('.')==-1:
                    result.add(each)
            if len(result)>0:
                updateArea += "// C++ Standard\n"
                for each in result:
                    updateArea += ("#include <" + each + ">\n")
                    cus.remove(each)

            if len(cus) > 0:
                updateArea += "// Custom header\n"
                for each in cus:
                    updateArea += ("#include \"" + each + "\"" + '\n')

        updateArea += '\n\n\n\n'
        updateArea += '// END CAAFINDER EDITION ZONE\n'
        # print(updateArea)
        content = content.replace(deleteArea,updateArea)
        f = open(headerPath, 'w',encoding='iso-8859-1')
        f.write(content)
        f.close()

# 修改Imakefile
def modifyImakefile(imakefile,res,cus = set()):

        moduel = os.path.split(os.path.split(imakefile)[0])[1].split('.')[0]
        content = '#======================================================================\n'
        content += '# Imakefile for module %s\n' %moduel
        content += '#======================================================================\n'
        content += '#  %s Creation: Code generated by the CAAFinder\n'%datetime.now().strftime('20%y-%m-%d')
        content += '#======================================================================\n'
        content += '\n\n'
        content += 'BUILT_OBJECT_TYPE=SHARED LIBRARY\n#BUILT_OBJECT_TYPE=LOAD MODULE\n'
        content += '\n\n'
        content += 'LINK_WITH = $(CAAFINDER_LINK_MODULES)'

        for each in cus:
            content += (' '+ each)
        content += '\n'

        content += "# DO NOT EDIT :: CAAFINDER WILL ADD CODE HERE\n"

        content += 'CAAFINDER_LINK_MODULES = \\\n'

        for each in res:
            content += '%s \\\n'%each
        content += '# END CAAFINDER EDITION ZONE\n'
        content += '\n\n'
        content += '#https://github.com/Gutier14/CAAFinder\n'
        content += '#email: geekluca@qq.com\n'

        f = open(imakefile,'w',encoding='iso-8859-1')
        f.write(content)
        f.close()

# 修改identityCard
def modifyIdentityCard(identitycardPath,res,cus = set()):

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
            if each not in container:
                child = etree.Element("prerequisite", name=each,access="Public")
                identityCard.append(child)

        for each in cus:
            if each not in container:
                identityCard[len(identityCard)-1].tail += '  '
                child = etree.Element("prerequisite", name=each,access="Public")
                child.tail = "\n"
                identityCard.append(child)

        f = open(identitycardPath,'w',encoding='iso-8859-1')
        f.write(etree.tostring(identityCard, xml_declaration=True).decode('iso-8859-1'))
        f.close()




if __name__=='__main__':
    a = workspace('GW')
    # a.completeModuel('GWSDDPartProofreader')
    # a.completeFramework('GWStruct')
    # a.info
    # a.backup()
    # a.complete()

    # parseIdentityCard('/Users/guti/Developer/CAAFinder/caafinder/GW_GWS_LC/GWStruct/IdentityCard/IdentityCard.xml')
    cpp = '/Users/guti/Developer/CAAFinder/caafinder/GW/GWStruct/GWSDDPartProofreader.m/src/GWSDDPartProofreaderCmd.cpp'
    header = '/Users/guti/Developer/CAAFinder/caafinder/GW/GWStruct/PrivateInterfaces/GWSDDPartProofreaderCmd.h'
    imakefile = '/Users/guti/Developer/CAAFinder/caafinder/GW/GWStruct/GWSDDPartProofreader.m/Imakefile.mk'
    identityCard = '/Users/guti/Developer/CAAFinder/caafinder/GW/GWStruct/IdentityCard/IdentityCard.xml'
    # res = parseIdentityCard(identityCard)
    a.completeUnit(cpp)
    # print(len(res))
    # print(res[0])
    # print(res[1])
    # modifyHeader(header,parseHeader(header)[0],parseHeader(header)[1])
    # modifyIdentityCard(identityCard,res[0],{'GWTest','fadaffff'})
    # modifyImakefile(imakefile,parseImakefile(imakefile)[0],parseImakefile(imakefile)[1])


