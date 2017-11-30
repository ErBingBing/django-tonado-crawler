# coding=utf-8
################################################################################################################
# @file: storage.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import os
import re

from utility.common import Common
from utility.fileutil import FileUtility
from configuration.environment.configure import SpiderConfigure
from configuration.constant import const, SPIDER_CHANNEL_S2
from configuration import constant
from log.spiderlog import Logger
import json

from utility.timeutility import TimeUtility

################################################################################################################
# @class：Storage
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Storage:

    # 各类信息存储位置模板
    STORAGE_LOCATION_FORMAT = '{parent}{child}/'

    # ETL结果文件存储路径
    SPIDER_STORE_FILENAME_FORMAT = '{path}/{channel}/{date}/{query}/{filename}'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.cache_path = Storage.getstoragelocation(const.SPIDER_OUTPUT_TEMP_PATH)
        self.channel = SpiderConfigure.getinstance().getchannel()
        self.query = SpiderConfigure.getinstance().getquery()
        self.type = SpiderConfigure.getinstance().gettype()

    ################################################################################################################
    # @functions：store
    # @param： none
    # @return：none
    # @note：存储信息到文件
    ################################################################################################################
    def store(self, url, info):
        pass

    ################################################################################################################
    # @functions：writeline
    # @param： none
    # @return：none
    # @note：输出一行信息到文件
    ################################################################################################################
    def writeline(self, url, line):
        Logger.getlogging().debug(line)
        FileUtility.writeline(self.getfilename(url), line)

    ################################################################################################################
    # @functions：getfilename
    # @param： URL
    # @return：文件名
    # @note：根据URL、以及当前的状态S1/S2 Query条件获取存储文件名
    ################################################################################################################
    def getfilename(self, url):
        # 渠道
        self.channel = SpiderConfigure.getinstance().getchannel()
        # S2查询信息
        self.query = SpiderConfigure.getinstance().getquery()
        # S2页面类型
        self.type = SpiderConfigure.getinstance().gettype()
        if self.channel == SPIDER_CHANNEL_S2:
            q = Common.md5(self.query)
        else:
            q = self.query
        return Storage.SPIDER_STORE_FILENAME_FORMAT.format(
            path = self.cache_path,
            date = TimeUtility.getcurrentdate(),
            channel = self.channel,
            query = q,
            filename = Common.md5(url))

    ################################################################################################################
    # @functions：removecachefile
    # @param： none
    # @return：none
    # @note：删除临时文件
    ################################################################################################################
    @staticmethod
    def removecachefile():
        cache = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_TEMPLATE_WORK_DIRECTORY)
        databackupfolder = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                       const.SPIDER_DATA_BACKUP_PATH) + TimeUtility.getcurrentdate(TimeUtility.TIMESTAMP_FORMAT)
        if FileUtility.exists(cache):
            FileUtility.move(cache, databackupfolder)
            FileUtility.rmdir(cache)
        limit = int(SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_OUTPUT_PATH_LIMIT))
        databackuppath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_DATA_BACKUP_PATH)
        if FileUtility.exists(databackuppath):
            validdate = TimeUtility.getdatebefore(limit, '%Y%m%d000000')
            for s in os.listdir(databackuppath):
                fullpath = os.path.join(databackuppath, s)
                #Logger.getlogging().info('remove cach folder ' + fullpath)
                #FileUtility.rmdir(fullpath)
                if s < validdate:
                    fullpath = os.path.join(databackuppath, s)
                    Logger.getlogging().info('remove cach folder ' + fullpath)
                    FileUtility.rmdir(fullpath)
    @staticmethod
    def mkcachedir():
        cache = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_TEMPLATE_WORK_DIRECTORY)
        FileUtility.rmdir(cache)
        FileUtility.mkdirs(cache)
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_WAIBU_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_TIEBA_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_URLS_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_DONE_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_JSON_TEMP_PATH))
        FileUtility.mkdirs(Storage.getstoragelocation(const.SPIDER_OUTPUT_TEMP_PATH))
      
        limit = int(SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_OUTPUT_PATH_LIMIT))
        outputpath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_OUTPUT_PATH)
        if FileUtility.exists(outputpath):
            validdate = TimeUtility.getuniformdatebefore(limit)
            for s in os.listdir(outputpath):
                if s < validdate:
                    fullpath = os.path.join(outputpath, s)
                    FileUtility.rmdir(fullpath)

    ################################################################################################################
    # @functions：getstoragelocation
    # @param： none
    # @return：none
    # @note：获取各类信息的存储路径
    ################################################################################################################
    @staticmethod
    def getstoragelocation(subpath):
        cache = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_TEMPLATE_WORK_DIRECTORY)
        return Storage.STORAGE_LOCATION_FORMAT.format(parent=cache, child=subpath)

    ################################################################################################################
    # @functions：urlencode
    # @str： none
    # @return：none
    # @note：Unicode转为UTF8的URL编码
    ################################################################################################################
    def urlencode(self, string):
        if string:
            if constant.URL_ENCODE_FLAG:
                return Common.urlenc(string.encode(constant.CHARSET_DEFAULT))
            else:
                return Storage.strip(string)
        else:
            return string

    @staticmethod
    def strip(value, replace=' '):
        if value:
            return re.sub('[\t\r\n ]+', replace, value)
        else:
            return value
