# -*- coding: utf-8 -*-
################################################################################################################
# @file: bilibiliquery.py
# @author: Han Luyang
# @date:  2017/09/11
# @note: bilibili查询模块
################################################################################################################
import json
import re
from bs4 import BeautifulSoup as bs
from configuration import constant
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
################################################################################################################
# @class：BilibiliS2Query
# @author：Han Luyang
# @date：2017/09/11
# @note：bilibili查询类
################################################################################################################
class BilibiliS2Query(SiteS2Query):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Han Luyang
    # @date: 2017/09/11
    # @note：BilibiliS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.bilibili.com/'
        self.queryUrl = 'http://search.bilibili.com/ajax_api/video?keyword={keyword}&page={page}&order=totalrank'
        #self.pageUrl = 'http://search.bilibili.com/all?keyword={keyword}&page={page}&order=totalrank'
        self.STEP_PAGES = None
        self.STEP_VIDEOS = 1
    ################################################################################################################
    # @functions：query
    # @param：共同模块传递的query信息（关键字）
    # @return：none
    # @author：Han Luyang
    # @date: 2017/09/11
    # @note：向共通模块传递通过关键字生成的原始url
    ################################################################################################################    
    def query(self, info):
        keyword = Common.urlenc(info)
        urls = [self.queryUrl.format(keyword=keyword, page=1)]
        self.__storeqeuryurllist__(urls, self.STEP_PAGES, {'keyword':keyword})
        
    ################################################################################################################
    # @functions：process
    # @param：共通模块传递url，原始url，step及自定义信息
    # @return：None
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：step1. 解析query原始url，产生分页url，并向共通模块传递 
    #        step2. 解析分页url，产生当页的所有url，并向共通模块传递
    ################################################################################################################
    def process(self, params):
        try:
            if params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_VIDEOS:
                self.step2(params)
        except:
            Logger.printexception()
    
    ################################################################################################################
    # @functions：step1
    # @param：共通模块传递url，原始url，step及自定义信息
    # @return：None
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：解析query原始url，产生分页url，并向共通模块传递
    ################################################################################################################
    def step1(self, params):
        try:
            keyword = params.customized['keyword']
            # html页面动态加载分页数，故采用分析json
            jsondata = json.loads(params.content)
            # 获取分页数
            pageNum = int(jsondata['numPages'])
            if pageNum >= self.maxpages:
                pageNum = self.maxpages
            pageUrlList = []
            # 拼接分页url
            for page in range(1, pageNum + 1):
                if page == 1:
                    self.step2(params)
                    continue
                queryUrl  = self.queryUrl.format(keyword=keyword, page=page)
                pageUrlList.append(queryUrl)
            # 传递分页url
            self.__storeqeuryurllist__(pageUrlList, self.STEP_VIDEOS, {'keyword':keyword})
        except:
            Logger.printexception()
        
    ################################################################################################################
    # @functions：step2
    # @param: 共通模块url，原始url，step及自定义信息
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：解析分页url，产生当页的所有url，并向共通模块传递
    ################################################################################################################
    def step2(self, params):
        keyword = params.customized['keyword']
        query = Common.urldec(keyword)
        jsondata = json.loads(params.content)
        # 获取分页数
        html = jsondata['html']          
        soup = bs(html,'html5lib')
        videoUrlList = []
        
        videoList = soup.select('li.video')
        for video in videoList:
            try:
                videoUrl = 'https:' + video.select_one('a').get('href')
                videoUrl = videoUrl.split('?')[0] + '/'
                title = video.select_one('a').get('title')
                pubtime = video.find(attrs={'class':'so-icon time'}).get_text().strip()
                if self.compareNow(TimeUtility.getuniformtime(pubtime)):
                    if self.checktitle(query, title):
                        videoUrlList.append(videoUrl)
                        self.__storeurl__(videoUrl, pubtime, SPIDER_S2_WEBSITE_VIDEO)
                    else:
                        Logger.log(videoUrl, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                else:
                    Logger.log(videoUrl, constant.ERRORCODE_WARNNING_NOMATCHTIME)                
            except:
                Logger.printexception()
        # 传递url
        #self.__storeurllist__(videoUrlList, SPIDER_S2_WEBSITE_VIDEO)