# -*- coding: utf-8 -*-

"""
# @file: mongodao.py
# @author: Sun Xinghua
# @date:  2017/6/6 14:16
# @version: Ver0.0.0.100
# @note: 
"""
import json

import pymongo
import time

from pymongo.errors import ConnectionFailure

from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from utility import const
from utility.fileutil import FileUtility

class MongoDAO:
    """
    # @class：MongoDAO
    # @author：Sun Xinghua
    # @date：2017/6/6 14:16
    # @note：
    """
    SPIDER_COLLECTION_NEWS = 'News'
    SPIDER_COLLECTION_NEWS_INDEX = 'id'
    SPIDER_COLLECTION_NEWS_ID = 'id'
    SPIDER_COLLECTION_NEWS_CID = 'cid'
    SPIDER_COLLECTION_NEWS_URL = 'url'
    SPIDER_COLLECTION_NEWS_QUERY = 'query'
    SPIDER_COLLECTION_NEWS_CHANNEL = 'channel'
    SPIDER_COLLECTION_NEWS_TYPE = 'type'
    SPIDER_COLLECTION_NEWS_ORIGINAL_URL = 'orignalurl'
    SPIDER_COLLECTION_NEWS_TITLE = 'title'
    SPIDER_COLLECTION_NEWS_BODY = 'body'
    SPIDER_COLLECTION_NEWS_PUBLISH_DATE = 'publishdate'
    SPIDER_COLLECTION_NEWS_MEDIA_NAME = 'meidaname'
    SPIDER_COLLECTION_NEWS_TOP_FLAG = 'topflag'
    SPIDER_COLLECTION_NEWS_CREATE_DATE = 'createdate'
    SPIDER_COLLECTION_NEWS_UPDATE_DATE = 'updatedate'
    SPIDER_COLLECTION_NEWS_IMAGE = 'image'
    SPIDER_COLLECTION_NEWS_IMAGE_URL = 'imageurl'
    SPIDER_COLLECTION_NEWS_RENEW = 'renew'
    SPIDER_COLLECTION_NEWS_CMTNUM = 'cmtnum'
    SPIDER_COLLECTION_NEWS_CLICKNUM = 'clickmum'
    SPIDER_COLLECTION_NEWS_FANSNUM = 'fansnum'
    SPIDER_COLLECTION_NEWS_VOTENUM = 'votenum'
    
    SPIDER_COLLECTION_IMAGE = 'Images'
    SPIDER_COLLECTION_IMAGE_ID_INDEX = 'id'
    SPIDER_COLLECTION_IMAGE_ID = 'id'
    SPIDER_COLLECTION_IMAGE_URL = 'imageurl'
    SPIDER_COLLECTION_IMAGE_FILE = 'imagefile'
    
    SPIDER_COLLECTION_CHANNEL = 'Channel'
    SPIDER_COLLECTION_CHANNEL_INDEX = 'cid'
    SPIDER_COLLECTION_CHANNEL_CID = 'cid'
    SPIDER_COLLECTION_CHANNEL_NAME = 'name'
    SPIDER_COLLECTION_CHANNEL_PATTERN = 'pattern'

    SPIDER_COLLECTION_WEBSITE = 'WebSite'
    SPIDER_COLLECTION_WEBSITE_INDEX = 'cid'
    SPIDER_COLLECTION_WEBSITE_CID = 'cid'
    SPIDER_COLLECTION_WEBSITE_URL = 'url'
    SPIDER_COLLECTION_WEBSITE_DOWNLOAD_MODE = 'downloadmode'

    SPIDER_COLLECTION_COMMENTS = 'Comments'
    SPIDER_COLLECTION_COMMENTS_INDEX = 'id'
    SPIDER_COLLECTION_COMMENTS_ID = 'id'
    SPIDER_COLLECTION_COMMENTS_URL = 'url'
    SPIDER_COLLECTION_COMMENTS_CONTENT = 'content'
    SPIDER_COLLECTION_COMMENTS_PUBLISH_DATE = 'publishdate'
    SPIDER_COLLECTION_COMMENTS_USER = 'user'
    SPIDER_COLLECTION_COMMENTS_CREATE_DATE = 'createdate'
    
    SPIDER_COLLECTION_DAOFLAG = 'daoflag'

    MAX_RETRY_TIMES = 3

    __instance = None

    @staticmethod
    def getinstance():
        if not MongoDAO.__instance:
            MongoDAO.__instance = MongoDAO()
        return MongoDAO.__instance


    def __init__(self):
        """
        # @functions：__init__
        # @param： none
        # @return：none
        # @note：mongodao类的构造器，初始化内部变量
        """
        self.ip = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_IP)
        self.port = int(SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_PORT))
        self.database = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_DATABASE)
        self.connected = False
        self.client = None
        self.retrytime = 0
        self.checktime = MongoDAO.gettime()
        self.createdatabase()

    def check(self):
        if not self.connected:
            return self.connect()
        else:
            if MongoDAO.gettime() - self.checktime > 300:
                self.checktime = MongoDAO.gettime()
                try:
                    # The ismaster command is cheap and does not require auth.
                    self.client.admin.command('ismaster')
                    return True
                except ConnectionFailure:
                    Logger.getlogging().error("Server not available")
                    self.close()
                    return self.connect()
            else:
                return True


    def connect(self):
        if not self.connected:
            self.client = pymongo.MongoClient(self.ip, self.port)
            try:
                # The ismaster command is cheap and does not require auth.
                self.client.admin.command('ismaster')
                self.connected = True
            except ConnectionFailure:
                print("Server not available")
                self.client.close()
                self.client = None
                self.connected = False
        return self.connected

    def close(self):
        if self.connected:
            self.client.close()
            self.client = None
            self.connected = False

    def insert(self, name, row, retrycount=0):
        if retrycount == 0:
            Logger.getlogging().debug('insert info {row} into table {name}'.format(row=json.dumps(row), name=name))
        if self.check():
            try:
                self.client[self.database][name].insert(row)
                return True
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.getlogging().error(row)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.insert(name, row, retrycount)

    def insertmany(self, name, rows, retrycount=0):
        for row in rows:
            Logger.getlogging().debug('insert info {row} into table {name}'.format(row=json.dumps(row), name=name))
        if self.check():
            try:
                self.client[self.database][name].insert(rows)
                return True
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.insertmany(name, row, retrycount)

    def find(self, name, cond={}, multi=True, keys={}, retrycount=0, size=50):
        if self.check():
            if multi:
                if keys:
                    return self.client[self.database][name].find(cond, keys).batch_size(size)
                return self.client[self.database][name].find(cond).batch_size(size)
            else:
                if keys:
                    return self.client[self.database][name].find_one(cond, keys)
                return self.client[self.database][name].find_one(cond)

    def count(self, name, cond, retrycount=0):
        if self.check():
            try:
                return self.client[self.database][name].find(cond).count()
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.count(name, cond, retrycount)

    def exist(self, name, cond, retrycount=0):
        if self.check():
            try:
                return self.client[self.database][name].find_one(cond) is not None
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.exist(name, cond, retrycount)

    def createcollection(self, name, keycolumn):
        if self.check():
            self.client[self.database][name].create_index([(keycolumn, pymongo.ASCENDING)], unique=True)

    def checkdatabase(self):
        if self.check():
            self.client[self.database][self.SPIDER_COLLECTION_CHANNEL].count()

    def createdatabase(self):
        self.createcollection(self.SPIDER_COLLECTION_NEWS, self.SPIDER_COLLECTION_NEWS_INDEX)
        self.createcollection(self.SPIDER_COLLECTION_CHANNEL, self.SPIDER_COLLECTION_CHANNEL_INDEX)
        self.createcollection(self.SPIDER_COLLECTION_WEBSITE, self.SPIDER_COLLECTION_WEBSITE_INDEX)
        self.createcollection(self.SPIDER_COLLECTION_COMMENTS, self.SPIDER_COLLECTION_COMMENTS_INDEX)
        self.createcollection(self.SPIDER_COLLECTION_IMAGE, self.SPIDER_COLLECTION_IMAGE_ID_INDEX)
        jsonfile = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_CHANNEL_CONFIG)
        self.loadfile(self.SPIDER_COLLECTION_CHANNEL, jsonfile)
        jsonfile = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_WEBSITE_CONFIG)
        self.loadfile(self.SPIDER_COLLECTION_WEBSITE, jsonfile)

    def update(self, name, where, update={}, one=True, retrycount=0, updateexp={}):
        if retrycount == 0:
            if updateexp:
                Logger.getlogging().debug('update {update} table {name} where {where}'.format(update=json.dumps(updateexp), name=name, where=json.dumps(where)))
            else:
                Logger.getlogging().debug('update {update} table {name} where {where}'.format(update=json.dumps(update), name=name, where=json.dumps(where)))
        if self.check():
            try:
                if one:
                    if updateexp:
                        self.client[self.database][name].update_many(where, updateexp)
                    else:
                        self.client[self.database][name].update_one(where, {'$set': update})
                else:
                    if updateexp:
                        self.client[self.database][name].update_many(where, updateexp)
                    else:
                        self.client[self.database][name].update_many(where, {'$set': update})
                return True
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.printexception()
                    return False
            self.update(name, where, update, one, retrycount + 1)

    def delete(self, name, where, one=True, retrycount=0):
        if self.check():
            try:
                if one:
                    self.client[self.database][name].delete_one(where)
                else:
                    self.client[self.database][name].delete_many(where)
                return True
            except:
                if retrycount == self.MAX_RETRY_TIMES:
                    Logger.printexception()
                    return False
            retrycount += 1
            self.delete(name ,where, one, retrycount)

    def loadfile(self, tablename, filepath, retrycount=0):
        try:
            self.delete(tablename, {}, False)
            jsonlist = []
            if not FileUtility.exists(filepath):
                return False
            with open(filepath, 'r') as fp:
                for line in fp.readlines():
                    if not line.strip():
                        continue
                    jsonlist.append(json.loads(line.strip()))
                if not jsonlist:
                    return False
                self.insert(tablename, jsonlist)
            return True
        except:
            if retrycount == self.MAX_RETRY_TIMES:
                Logger.printexception()
                return False
        retrycount += 1
        return self.loadfile(tablename, filepath, retrycount)

    def count(self, tablename, cond, retrycount=0):
        try:
            return self.find(tablename, cond).count()
        except:
            if retrycount == self.MAX_RETRY_TIMES:
                Logger.printexception()
                return None
        retrycount += 1
        self.count(tablename, cond, retrycount)


    @staticmethod
    def gettime():
        return int(time.time())

class BasicInfo:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：PageBasicInfo初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.id = ''
        # query
        self.query = ''   
        # 渠道
        self.channel = ''
        # 类型
        self.type = ''        
        # URL
        self.url = ''
        # 标题
        self.title = ''
        # 正文 / 主贴
        self.body = ''
        # 评论（内容） / 回复（内容）
        # 评论量
        self.cmtnum = -1
        # 阅读量 / 播放量 增量
        self.clicknum = -1
        # 点赞量
        self.votenum = -1
        # 粉丝量 / 订阅量
        self.fansnum = -1
        # 发布时间
        self.pubtime = None
        # 抓取时间
        #self.crawlertime = SpiderConfigure.getinstance().starttime()
        # 本次运行spider开始时间createtime
        self.createtime = SpiderConfigure.getinstance().starttime()
        self.key1 = ''
        self.key2 = ''
        self.key3 = ''
        self.key4 = ''
        self.key5 = ''
        self.key6 = ''
        self.key7 = ''
        self.key8 = ''        
        self.key9 = ''
        self.key10 = ''

import os

if __name__ == '__main__':
    os.chdir('..')
    # dao = MongoDAO()
    # dao.createdatabase()
    # dao.close()
    abc = [
                {MongoDAO.SPIDER_COLLECTION_CHANNEL_CID:300, MongoDAO.SPIDER_COLLECTION_CHANNEL_NAME:u'新浪', MongoDAO.SPIDER_COLLECTION_CHANNEL_PATTERN:r'http[s]://.*\.sina\.com.*'},
                {MongoDAO.SPIDER_COLLECTION_CHANNEL_CID:301, MongoDAO.SPIDER_COLLECTION_CHANNEL_NAME:u'搜狐', MongoDAO.SPIDER_COLLECTION_CHANNEL_PATTERN:r'http[s]://.*\.sohu\.com.*'},
                {MongoDAO.SPIDER_COLLECTION_CHANNEL_CID:302, MongoDAO.SPIDER_COLLECTION_CHANNEL_NAME:u'网易', MongoDAO.SPIDER_COLLECTION_CHANNEL_PATTERN:r'http[s]://.*\.163\.com.*'}
            ]
    print json.dumps(abc)
