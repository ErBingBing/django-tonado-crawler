# coding=utf-8
################################################################################################################
# @file: fileutil.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import os
import shutil
import re
import codecs

################################################################################################################
# @class：FileUtility
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class FileUtility:

    # file cache
    __filescache = {}
    __filelines = {}

    ################################################################################################################
    # @functions：getfilelist
    # @param： dir搜索文件夹
    # @param： fileList既有的文件列表
    # @return：文件列表
    # @note：从文件夹dir中去所有的文件列表，包括子目录下的
    ################################################################################################################
    @staticmethod
    def getfilelist(dir, filelist=[]):
        newdir = dir
        if os.path.isfile(dir):
            filelist.append(dir.decode('gbk'))
        elif os.path.isdir(dir):
            for s in os.listdir(dir):
                newdir = os.path.join(dir, s)
                FileUtility.getfilelist(newdir, filelist)
        return filelist

    ################################################################################################################
    # @functions：exists
    # @param： 文件路径
    # @return：文件存在返回True，否则返回False
    # @note：判断file是否存在
    ################################################################################################################
    @staticmethod
    def exists(file):
        return os.path.exists(file) or file in FileUtility.__filescache

    ################################################################################################################
    # @functions：getfilesize
    # @param： 文件路径
    # @return：文件大小
    # @note：
    ################################################################################################################
    @staticmethod
    def getfilesize(filepath):
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0

    ################################################################################################################
    # @functions：getfilename
    # @param： 文件全路径
    # @return：文件名
    # @note：从文件全路径中获取文件名
    ################################################################################################################
    @staticmethod
    def getfilename(filepath):
        return os.path.basename(filepath)

    ################################################################################################################
    # @functions：copy
    # @param： src源文件
    # @param： dsc目标文件
    # @return：none
    # @note：复制文件从src到dsc
    ################################################################################################################
    @staticmethod
    def copy(src, dsc):
        shutil.copy(src, dsc)

    ################################################################################################################
    # @functions：move
    # @param： src源文件
    # @param： dsc目标文件
    # @return：none
    # @note：移动文件从src到dsc
    ################################################################################################################
    @staticmethod
    def move(src, dsc):
        shutil.move(src, dsc)

    ################################################################################################################
    # @functions：remove
    # @param： 路径
    # @return：none
    # @note：删除文件
    ################################################################################################################
    @staticmethod
    def remove(path):
        if FileUtility.exists(path):
            os.remove(path)

    ################################################################################################################
    # @functions：find
    # @param： directory路径
    # @param： regex正则表达式
    # @return：匹配的文件列表
    # @note：从文件夹中搜索符合正则regex的文件列表
    ################################################################################################################
    @staticmethod
    def find(directory, regex):
        file_list = FileUtility.getfilelist(directory, [])
        match_files = []
        for f in file_list:
            if re.search(regex, f):
                match_files.append(f)
        return match_files

    ################################################################################################################
    # @functions：writeline
    # @param： 文件路径
    # @return：none
    # @note：想文件filepath中输出一行
    ################################################################################################################
    @staticmethod
    def writeline(filepath, line):
        # if no dir create dir TODO
        if filepath in FileUtility.__filelines:
            FileUtility.__filelines[filepath] += 1
        else:
            FileUtility.__filelines[filepath] = 1
        if filepath not in FileUtility.__filescache:
            FileUtility.__filescache[filepath] = []
        FileUtility.__filescache[filepath].append(str(line))
        if len(FileUtility.__filescache[filepath]) > 100:
            #FileUtility.writelines(filepath, FileUtility.__filescache[filepath])
            lines = FileUtility.__filescache[filepath]
            path, name = os.path.split(filepath)
            FileUtility.mkdirs(path)
            with open(filepath, 'a') as fp:
                fp.write('\n'.join(lines))
                fp.write('\n')
            FileUtility.__filescache[filepath] = []

    ################################################################################################################
    # @functions：writeline
    # @param： 文件路径
    # @return：none
    #  @note：想文件filepath中输出一行
    ################################################################################################################
    @staticmethod
    def writelines(filepath, lines):
        if filepath in FileUtility.__filelines:
            FileUtility.__filelines[filepath] += len(lines)
        else:
            FileUtility.__filelines[filepath] = len(lines)
        path, name = os.path.split(filepath)
        FileUtility.mkdirs(path)
        with open(filepath, 'a') as fp:
            fp.write('\n'.join(lines))
            fp.write('\n')

    @staticmethod
    def geturlfilelines(filepath):
        if filepath in FileUtility.__filelines:
            return FileUtility.__filelines[filepath]
        return 0

    ################################################################################################################
    # @functions：removefiles
    # @param： 文件夹路径
    # @return：none
    # @note：删除文件夹下所有的文件
    ################################################################################################################
    @staticmethod
    def removefiles(path):
        for file in FileUtility.getfilelist(path, []):
            FileUtility.remove(file)

    ################################################################################################################
    # @functions：mkdirs
    # @param： path路径
    # @return：none
    # @note：创建文件夹
    ################################################################################################################
    @staticmethod
    def mkdirs(path):
        if not FileUtility.exists(path):
            os.makedirs(path)

    @staticmethod
    def rmdir(path):
        shutil.rmtree(path, True)

    @staticmethod
    def flush():
        for filepath in FileUtility.__filescache.keys():
            if FileUtility.__filescache[filepath]:
                FileUtility.writelines(filepath, FileUtility.__filescache[filepath])
                FileUtility.__filescache[filepath] = []

    @staticmethod
    def getfilelines(filepath):
        if FileUtility.exists(filepath):
            with open(filepath, 'r') as fp:
                return len(fp.readlines())
        return 0
    
    @staticmethod
    def readlines(filepath):
        lines = []
        with open(filepath, 'r') as fp:
            firstline = True
            for strline in fp.readlines():
                if firstline:
                    firstline = False
                    if strline[:3] == codecs.BOM_UTF8:
                        strline = strline[3:]
                strline = strline.strip()
                if not strline:
                    continue
                lines.append(strline)    
        return lines

if __name__ == '__main__':
    print os.path.split('E:/2016/Tencent/spider/data/urls')
