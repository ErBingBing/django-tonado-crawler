# -*- coding: utf-8 -*-

"""
# @file: urlmanager.py
# @author: Sun Xinghua
# @date:  2017/6/5 9:51
# @version: Ver0.0.0.100
# @note: 
"""

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from urlfilemanager import URLFileManager
from utility.common import Common
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility


class URLManager:
    # 单实例，URLManager实例map
    __instancemap = {}
    waibustorage = {}
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        # URL上下文，url: urlcontext
        self.urlcontextdict = {}

    ################################################################################################################
    # @functions：getinstance
    # @param： none
    # @return：none
    # @note：返回单实例
    ################################################################################################################
    @staticmethod
    def getinstance():
        channel = SpiderConfigure.getinstance().getchannel()
        if channel == constant.SPIDER_CHANNEL_S2:
            key = SpiderConfigure().getquery()
        else:
            key = channel
        if key not in URLManager.__instancemap:
            URLManager.__instancemap[key] = URLManager()
        return URLManager.__instancemap[key]

    ################################################################################################################
    # @functions：getinstances
    # @param： none
    # @return：当前URLManager实例
    # @note：获取当前URLManager实例
    ################################################################################################################
    @staticmethod
    def getinstances():
        return URLManager.__instancemap

    ################################################################################################################
    # @functions：storeurl
    # @url： URL
    # @urlcontext： URL上下文
    # @return：none
    # @note：保存URL上下文
    ################################################################################################################
    def storeurl(self, url, urlcontext, request=constant.REQUEST_TYPE_COMMON):
        if url.strip():
            urlfile = URLFileManager.getinstance().geturlfilepath(request)
            if FileUtility.geturlfilelines(urlfile) + 1 > URLFileManager.URL_FILE_LINES_MAX_NUMBER:
                URLFileManager.getinstance().generateurlfilepath()
                urlfile = URLFileManager.getinstance().geturlfilepath(request)
            FileUtility.writeline(urlfile, url)
            key = Common.md5(url.strip())
            if key not in self.urlcontextdict:
                self.urlcontextdict[key] = []
            self.urlcontextdict[key].append(urlcontext)

    ################################################################################################################
    # @functions：storeurls
    # @url： URL
    # @urlcontext： URL上下文
    # @return：none
    # @note：保存URL上下文
    ################################################################################################################
    def storeurls(self, urls, request=constant.REQUEST_TYPE_COMMON):
        urlfile = URLFileManager.getinstance().geturlfilepath(request)
        if FileUtility.geturlfilelines(urlfile) + len(urls) > URLFileManager.URL_FILE_LINES_MAX_NUMBER:
            URLFileManager.getinstance().generateurlfilepath()
            urlfile = URLFileManager.getinstance().geturlfilepath(request)
        FileUtility.writelines(urlfile, urls)

    ################################################################################################################
    # @functions：geturlcontext
    # @param url： URL
    # @return：URL上下文
    # @note：获取URL上下文
    ################################################################################################################
    def geturlcontext(self, url):
        if self.urlcontextdict[Common.md5(url)]:
            return self.urlcontextdict[Common.md5(url)].pop()

    ################################################################################################################
    # @functions：geturlcontext
    # @param url： URL
    # @return：URL上下文
    # @note：获取URL上下文
    ################################################################################################################
    def seturlcontext(self, url, urlcontext):
        key = Common.md5(url.strip())
        if key not in self.urlcontextdict:
            self.urlcontextdict[key] = []
        self.urlcontextdict[key].append(urlcontext)

    ################################################################################################################
    # @functions：hasurl
    # @param： URL
    # @return：True 存在/False 不存在
    # @note：是否存在该URL上下文
    ################################################################################################################
    def exist(self, url):
        if self.urlcontextdict.has_key(Common.md5(url)):
            if self.urlcontextdict[Common.md5(url)]:
                return True
        return False
    

################################################################################################################
# @class：URLContext
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class URLContext:
    S1_MAIN_BODY = 0
    S1_COMMENTS = 1
    S2_QUERY = 2
    S3_HOME_PAGE = 3

    def __init__(self):
        self.originalurl = None
        self.url = None
        self.type = URLContext.S1_MAIN_BODY
        self.step = None
        self.customized = {}

        