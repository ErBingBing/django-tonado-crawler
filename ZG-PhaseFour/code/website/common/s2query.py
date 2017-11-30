# -*- coding: utf-8 -*-
################################################################################################################
# @file: s2query.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import json
import urllib
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger 
################################################################################################################
# @class：SiteS2Query
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from storage.urlmanager import URLManager, URLContext
from utility import const
from utility.common import Common
from storage.newsstorage import NewsStorage, PageBasicInfo
from utility.timeutility import TimeUtility 

class SiteS2Query:
    # refer url
    REFER_URL = 'referurl'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SiteS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        self.fakeoriginalurl = 'http://query.website.com/'
        self.querylastdays = int(SpiderConfigure.getinstance().getlastdays())
        self.website = self
        self.maxpages = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN,
                                                      const.SPIDER_S2_MAX_QUERY_PAGES))

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        pass

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        pass

    ################################################################################################################
    # @functions：storeurllist
    # @urllist： S2查询结果的URL列表
    # @return：none
    # @note：SiteS2Query， 保存S2查询结果的URL列表（例如视频列表）
    ################################################################################################################
    def __storeurllist__(self, urllist, type=constant.SPIDER_S2_WEBSITE_VIDEO, referlist=[]):
        count = 0
        index = 0
        for url in urllist:
            params = PageBasicInfo()
            params.url = url
            params.type = type
            #检查是否在cold数据库中
            #如果不在cold数据库中则插入hot数据库中
            if not NewsStorage.exist_cold(url):
                NewsStorage.seturlinfos(params)
            #params = {constant.SPIDER_S2_WEBSITE_TYPE: type,
            #constant.SPIDER_CHANNEL: constant.SPIDER_CHANNEL_S1}            
            #url = url.strip()
            #if not URLManager.getinstance().exist(url):
            #count += 1
            #if referlist:
            #params[SiteS2Query.REFER_URL] = referlist[index]
            #urlcontext = URLContext()
            #urlcontext.url = url
            #urlcontext.type = URLContext.S1_MAIN_BODY
            #urlcontext.originalurl = url
            #urlcontext.customized = params
            #URLManager.getinstance().storeurl(url, urlcontext, constant.REQUEST_TYPE_WEBKIT) 
            index += 1
    #----------------------------------------------------------------------
    def __storeurl__(self, url, publishdate, type=constant.SPIDER_S2_WEBSITE_VIDEO):
        params = PageBasicInfo()
        params.url = url
        params.type = type
        params.pubtime = publishdate
        #检查是否在cold数据库中
        #如果不在cold数据库中则插入hot数据库中
        if not NewsStorage.exist_cold(url):
            NewsStorage.seturlinfos(params)
   
    ################################################################################################################
    # @functions：storeqeuryurllist
    # @urllist： 完成S2查询的URL列表
    # @return：none
    # @note：SiteS2Query， 保存S2查询的URL列表
    ################################################################################################################
    def __storeqeuryurllist__(self, urllist, step, customized={}):
        for url in urllist:
            customized[constant.SPIDER_CHANNEL] = constant.SPIDER_CHANNEL_S2
            urlcontext = URLContext()
            urlcontext.url = url
            urlcontext.originalurl = self.fakeoriginalurl
            urlcontext.type = URLContext.S2_QUERY
            urlcontext.step = step
            urlcontext.customized = customized
            URLManager.getinstance().storeurl(url, urlcontext)

    ################################################################################################################

    # @functions：storeqeuryurl
    # @urllist： 完成S2查询的URL列表,post方法
    # @return：none
    # @note：SiteS2Query， 保存S2查询的URL列表
    ################################################################################################################
    def __storeqeuryurl__(self, url, step, data, customized={}):
        customized[constant.SPIDER_CHANNEL] = constant.SPIDER_CHANNEL_S2
        urlcontext = URLContext()
        urlcontext.url = json.dumps({'url': url, 'data': urllib.urlencode(data)})
        urlcontext.originalurl = self.fakeoriginalurl
        urlcontext.step = step
        urlcontext.type = URLContext.S2_QUERY
        urlcontext.customized = customized
        URLManager.getinstance().storeurl(urlcontext.url, urlcontext, constant.REQUEST_TYPE_POST)

    ################################################################################################################
    # @functions：setwebsite
    # @website： 主站
    # @return：none
    # @note：设置主站
    ################################################################################################################
    def setwebsite(self, website):
        self.website = website
        
    #----------------------------------------------------------------------
    def querykey2urlenc(self, info, utf82gbk=True):
        """"""
        if utf82gbk:
            info = Common.urlenc(Common.trydecode(info).encode('gbk'))
            return info
        return Common.urlenc(info)
    
    #----------------------------------------------------------------------
    def compareNow(self, curtime, days=None):
        if not days:
            days = self.querylastdays
        return TimeUtility.compareNow(TimeUtility.getuniformtime(curtime), days)
    
    #----------------------------------------------------------------------
    def checktitle(self, query, title):
        return Common.checktitle(query, title)
        


            
        
        
        
        
