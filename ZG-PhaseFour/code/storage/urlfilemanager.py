# -*- coding: utf-8 -*-

"""
# @file: urlfilemanager.py
# @author: Sun Xinghua
# @date:  2017/6/5 9:51
# @version: Ver0.0.0.100
# @note: 
"""
import time

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from storage import Storage
from utility import const
from utility.common import Common
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility


class URLFileManager:
    # 时间格式
    FILE_SUFFIX_FORMAT = '%H%M%S'
    # URL文件格式模板
    URLS_FILE_PATTERN = '{path}{channel}_{query}_{ts}'
    # max url file lines
    URL_FILE_LINES_MAX_NUMBER = 500
    # instance
    __instance = None

    def __init__(self):
        # 每一次设置query和channel时设置上传文件名；下载后设置重新设置下载文件名
        self.urlsfile = ''
        self.urlsfilemap = {}
        self.urlfiletimestamp = 0
        self.tempurldir = Storage.getstoragelocation(const.SPIDER_URLS_TEMP_PATH)
        #self.generateurlfilepath()

    @staticmethod
    def getinstance():
        if URLFileManager.__instance is None:
            URLFileManager.__instance = URLFileManager()
        return URLFileManager.__instance

    ################################################################################################################
    # @functions：generateurlfilename
    # @param： filename
    # @return：URL文件
    # @note：生成URL文件，并设置其上下文信息
    ################################################################################################################
    def generateurlfilepath(self, retrytimes=0):
        context = URLFileContext()
        context.channel = SpiderConfigure.getinstance().getchannel()
        context.query = SpiderConfigure.getinstance().getquery()
        context.retry = retrytimes
        # 防止生成相同的URL文件，等待1秒后重新获取时间戳
        if self.urlfiletimestamp == int(time.time()):
            time.sleep(1)
        self.urlfiletimestamp = int(time.time())
        self.urlsfile = URLFileManager.URLS_FILE_PATTERN.format(
            path=self.tempurldir,
            channel=context.channel,
            query=Common.md5(context.query),
            ts=self.urlfiletimestamp)
        context.filename = self.urlsfile
        self.urlsfilemap[FileUtility.getfilename(self.urlsfile)] = context
        Logger.getlogging().info(self.urlsfile)
        return self.urlsfile

    ################################################################################################################
    # @functions：geturlfilecontext
    # @param： filename
    # @return：文件名上下文
    # @note：根据文件名返回上下文
    ################################################################################################################
    def geturlfilecontext(self, filename):
        for key in self.urlsfilemap.keys():
            if RegexUtility.match(key + '.*', filename):
                return self.urlsfilemap[key]

    ################################################################################################################
    # @functions：geturlfilecontext
    # @param： filename
    # @return：文件名上下文
    # @note：根据文件名返回上下文
    ################################################################################################################
    def updateurlfilecontext(self, filename, urlfilecontext):
        for key in self.urlsfilemap.keys():
            if RegexUtility.match(key + '.*', filename):
                self.urlsfilemap[key] = urlfilecontext
                break
        else:
            self.urlsfilemap[filename] = urlfilecontext
    ################################################################################################################
    # @functions：geturlfiles
    # @param： none
    # @return：所有的URL文件
    # @note：获取所有的URL文件
    ################################################################################################################
    def geturlfiles(self):
        return FileUtility.getfilelist(self.tempurldir, [])

    ################################################################################################################
    # @functions：geturlfilepath
    # @param： none
    # @return：URL文件名
    # @note：获取当前URL文件名
    ################################################################################################################
    def geturlfilepath(self, request=constant.REQUEST_TYPE_COMMON):
        suffix = ''
        if request == constant.REQUEST_TYPE_WEBKIT:
            suffix = constant.WEBKIT_FILE_SUFFIX
        elif request == constant.REQUEST_TYPE_POST:
            suffix = constant.POST_FILE_SUFFIX
        elif request == constant.REQUEST_TYPE_IMG:
            suffix = constant.IMG_FILE_SUFFIX
        return self.urlsfile + suffix


class URLFileContext:
    def __init__(self):
        # filename
        self.filename = ''
        # channel
        self.channel = ''
        # query
        self.query = ''
        # retry flag
        self.retry = 0
        # download mod
        #self.downloader = constant.SPIDER_DOWNLOADER_REMOTE
