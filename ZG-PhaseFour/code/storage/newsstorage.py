# -*- coding: utf-8 -*-

"""
# @file: cmtstorage.py
# @author: Jiang Siwei
# @date:  2017/8/28 16:09
# @version: Ver0.0.0.100
# @note:
"""
#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())

import time
import urllib
import re
from dao.sqldao import SQLDAO
from log.spiderlog import Logger
from utility.common import Common
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility
from configuration.constant import CHARSET_UTF8
from configuration import constant
from configuration.environment.configure import SpiderConfigure 

class NewsStorage:
    NEWS_FORMAT = u'{channel}\t{query}\t{cmtnum}\t{clicknum}\t{fansnum}\t{votenum}\t{publishdate}\t{createdate}\t{url}'
    LOCALMACHINEFLAG=SpiderConfigure.getinstance().localmachineflag()
    
    @staticmethod
    def seturlinfo(url, key=None, value=None, data={}):
        id = NewsStorage.getid(url)
        if data:
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: id}, data)   
            return
        if SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE == key:
            value = TimeUtility.getuniformtime(value)
        if NewsStorage.exist(url):
            doc = NewsStorage.getdoc(url)
            tempvalue = doc.get(key,'')
            if tempvalue != value:
                data = {key: value, 
                        SQLDAO.SPIDER_TABLE_NEWS_UPDATE_DATE: SQLDAO.gettime()}
                SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: id}, data)                             
        else:
            data = {}
            data[SQLDAO.SPIDER_TABLE_NEWS_ID] = id
            data[SQLDAO.SPIDER_TABLE_NEWS_URL] = url
            data[SQLDAO.SPIDER_TABLE_NEWS_QUERY] = SpiderConfigure.getinstance().getquery()
            data[SQLDAO.SPIDER_TABLE_NEWS_CHANNEL] = SpiderConfigure.getinstance().getchannel()
            data[SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG] = NewsStorage.LOCALMACHINEFLAG
            data[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE] = SpiderConfigure.getinstance().starttime()   
            data[key] = value
            data[SQLDAO.SPIDER_TABLE_NEWS_UPDATE_DATE] = SQLDAO.gettime()
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_NEWS, SQLDAO.SPIDER_TABLE_NEWS_KEYS, SQLDAO.getvaluesfromkeys(data))

    @staticmethod
    def seturlinfos(params):
        id = NewsStorage.getid(params.url)
        if NewsStorage.exist(params.url):
            doc = NewsStorage.getdoc(params.url)           
            data = {}
            #data[SQLDAO.SPIDER_TABLE_NEWS_TYPE] = params.type
            data[SQLDAO.SPIDER_TABLE_NEWS_TITLE] = Common.strfilter(params.title)
            if params.type != constant.SPIDER_S2_WEBSITE_VIDEO:
                data[SQLDAO.SPIDER_TABLE_NEWS_BODY] = Common.strfilter(params.body)
            if doc.get(SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE, TimeUtility.getintformtime(0)) == TimeUtility.getintformtime(0):
                data[SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE] = TimeUtility.getuniformtime(params.pubtime)
            data[SQLDAO.SPIDER_TABLE_NEWS_CMTNUM] = params.cmtnum
            data[SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM] = params.clicknum
            data[SQLDAO.SPIDER_TABLE_NEWS_FANSNUM] = params.fansnum
            data[SQLDAO.SPIDER_TABLE_NEWS_VOTENUM] = params.votenum
            data[SQLDAO.SPIDER_TABLE_NEWS_UPDATE_DATE] = SQLDAO.gettime()            
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: id}, data)
        else:
            data = {}
            data[SQLDAO.SPIDER_TABLE_NEWS_TYPE] = params.type
            data[SQLDAO.SPIDER_TABLE_NEWS_TITLE] = Common.strfilter(params.title)
            if params.type != constant.SPIDER_S2_WEBSITE_VIDEO:
                data[SQLDAO.SPIDER_TABLE_NEWS_BODY] = Common.strfilter(params.body)
            data[SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE] = TimeUtility.getuniformtime(params.pubtime)
            data[SQLDAO.SPIDER_TABLE_NEWS_CMTNUM] = params.cmtnum
            data[SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM] = params.clicknum
            data[SQLDAO.SPIDER_TABLE_NEWS_FANSNUM] = params.fansnum
            data[SQLDAO.SPIDER_TABLE_NEWS_VOTENUM] = params.votenum
            data[SQLDAO.SPIDER_TABLE_NEWS_UPDATE_DATE] = SQLDAO.gettime()
            
            data[SQLDAO.SPIDER_TABLE_NEWS_ID] = id
            data[SQLDAO.SPIDER_TABLE_NEWS_URL] = params.url
            data[SQLDAO.SPIDER_TABLE_NEWS_QUERY] = params.query
            data[SQLDAO.SPIDER_TABLE_NEWS_CHANNEL] = params.channel
            data[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE] = params.createtime
            data[SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG] = NewsStorage.LOCALMACHINEFLAG
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_NEWS, SQLDAO.SPIDER_TABLE_NEWS_KEYS, SQLDAO.getvaluesfromkeys(data))
        
    @staticmethod
    def storeurl(url):
        id = NewsStorage.getid(url)
        if not NewsStorage.exist(url):
            data = {}
            data[SQLDAO.SPIDER_TABLE_NEWS_ID] = id
            data[SQLDAO.SPIDER_TABLE_NEWS_URL] = url
            data[SQLDAO.SPIDER_TABLE_NEWS_QUERY] = SpiderConfigure.getinstance().getquery()
            data[SQLDAO.SPIDER_TABLE_NEWS_CHANNEL] = SpiderConfigure.getinstance().getchannel()
            data[SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG] = NewsStorage.LOCALMACHINEFLAG
            data[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE] = SpiderConfigure.getinstance().starttime()
            data[SQLDAO.SPIDER_TABLE_NEWS_UPDATE_DATE] = SQLDAO.gettime()
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_NEWS, SQLDAO.SPIDER_TABLE_NEWS_KEYS, SQLDAO.getvaluesfromkeys(data))

    @staticmethod
    def exist(url):
        if NewsStorage.getcount(url):
            return True
        return False
    #----------------------------------------------------------------------
    @staticmethod
    def exist_cold(url):
        results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS_COLD, {SQLDAO.SPIDER_TABLE_NEWS_URL:url})
        if results:
            return True
        return False
        
    @staticmethod
    def getcount(url):
        id = NewsStorage.getid(url)
        return SQLDAO.getinstance().count(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: id})
                                       

    #Newstorage表格中的id，由query_url_starttime的md5值组成
    @staticmethod
    def getid(url):
        idformat = '{machine}_{query}_{url}_{starttime}'
        id = idformat.format(machine=NewsStorage.LOCALMACHINEFLAG,
                             query=Common.urlenc(SpiderConfigure.getinstance().getquery()), 
                             url=Common.urlenc(url), 
                             starttime=SpiderConfigure.getinstance().starttime())
        return Common.md5(id)
    @staticmethod
    def getdoc(url):
        value = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS,
                                          {SQLDAO.SPIDER_TABLE_NEWS_ID: NewsStorage.getid(url)},
                                          multi=False)
        return SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, value)
        
    @staticmethod
    def gettitle(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_TITLE, '')
    
    @staticmethod
    def getcmtnum(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_CMTNUM, -1)  
    
    @staticmethod
    def getclicknum(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM, -1)

    @staticmethod
    def getvotenum(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_VOTENUM, -1)
    
    @staticmethod
    def getfansnum(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_FANSNUM, -1)
    
    @staticmethod
    def getpublishdate(url):
        data = NewsStorage.getdoc(url)
        return data.get(SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE, TimeUtility.getuniformtime(0))
    
    @staticmethod
    def settitle(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_TITLE, value) 
        
    @staticmethod
    def setcmtnum(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_CMTNUM, value)
    
    @staticmethod
    def setclicknum(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM, value)
    
    @staticmethod
    def setvotenum(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_VOTENUM, value)      
        
    @staticmethod
    def setfansnum(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_FANSNUM, value)      

    @staticmethod
    def setbody(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_BODY, Common.strfilter(value))    
        
    @staticmethod
    def setpublishdate(url, value):
        NewsStorage.seturlinfo(url, SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE, value)      
    #----------------------------------------------------------------------
    @staticmethod    
    def show():
        u'{channel}\t{query}\t{cmtnum}\t{clicknum}\t{fansnum}\t{votenum}\t{publishdate}\t{createdate}\t{url}'
        Logger.getlogging().debug('Now, Results Extract From Database Showing: ')
        Logger.getlogging().debug(u'channel\tquery\tcmtnum\tclicknum\tfansnum\tvotenum\tpublishdate\tcreatedate\turl')
        alldata = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, 
                                        {SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE:SpiderConfigure.getinstance().starttime()})
        for data in alldata:
            dictdata = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, data)
            string = NewsStorage.NEWS_FORMAT.format(channel = dictdata[SQLDAO.SPIDER_TABLE_NEWS_CHANNEL],
                                                    query   = dictdata[SQLDAO.SPIDER_TABLE_NEWS_QUERY],
                                                    cmtnum  = dictdata[SQLDAO.SPIDER_TABLE_NEWS_CMTNUM],
                                                    clicknum= dictdata[SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM],
                                                    fansnum = dictdata[SQLDAO.SPIDER_TABLE_NEWS_FANSNUM],
                                                    votenum = dictdata[SQLDAO.SPIDER_TABLE_NEWS_VOTENUM],
                                                    publishdate= dictdata[SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE],
                                                    createdate = dictdata[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE],
                                                    url     = dictdata[SQLDAO.SPIDER_TABLE_NEWS_URL]
                                                    )
            Logger.getlogging().debug(string)
################################################################################################################
# @class：PageBasicInfo
# @author：Jiang Siwei
# @date：2017-08-30
# @note：
################################################################################################################
class PageBasicInfo:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：PageBasicInfo初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.id = ''
        # query
        self.query = SpiderConfigure.getinstance().getquery()    
        # 渠道
        self.channel = SpiderConfigure.getinstance().getchannel() 
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
        self.pubtime = TimeUtility.getintformtime(0)
        # createtime
        self.createtime = SpiderConfigure.getinstance().starttime()
        

if __name__ == '__main__':
    url='http://www.sohu.com/'
    info = PageBasicInfo()
    info.url = url
    NewsStorage.seturlinfos(info)
    print NewsStorage.getdoc(url)