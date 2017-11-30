# -*- coding: utf-8 -*-
################################################################################################################
# @file: acfunquery.py
# @author: Merlin.W.ouyang
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/01/12
# @note:网站域名更新升级，原地址：http://www.acfun.tv/ 升级后地址：http://www.acfun.cn/
#       取urllist逻辑没变,修改了S2_URL,注释掉params.content=params.content.replace('system.tv=','')
################################################################################################################
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from configuration.environment.configure import SpiderConfigure
import json
import math
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.timeutility import TimeUtility
from configuration import constant
################################################################################################################
# @class：AcFunQuery
# @author：Merlin.W.ouyang
# @date：2016/11/22
# @note：
################################################################################################################
########################################################################
class  S2Query(SiteS2Query):
    # ac视频相关搜索接口
    # S2_URL = 'http://search.aixifan.com/search?q={key}&pageSize={pagesize}&pageNo={pageno}&aiCount=3&spCount=3&type=2'
    # ac视频最新搜索接口
    S2_URL = 'http://search.aixifan.com/search?q={key}&isArticle=1&sys_name=pc&format=system.searchResult&pageSize={pagesize}&pageNo={pageno}&aiCount=3&spCount=3&type=2&isWeb=1&sortField=releaseDate'
    STEP_1 = 1
    STEP_2 = 2
    PAGE_SIZE = 30
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：AcFunQuery，初始化内部变量
    ################################################################################################################
    #----------------------------------------------------------------------
    def __init__(self):
        SiteS2Query.__init__(self)
        self.r = RegexUtility()
        self.fakeoriginalurl='http://www.acfun.cn/v/'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()       
        
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################        
    #----------------------------------------------------------------------
    def query(self,info):
        querykey=Common.urlenc(info)
        query_url = [S2Query.S2_URL.format(key=querykey, pagesize=self.PAGE_SIZE, pageno=1)]
        self.__storeqeuryurllist__(query_url, self.STEP_1, {'key':querykey})
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    #----------------------------------------------------------------------
    def  process(self,params):
        if params.step == S2Query.STEP_1:
            self.step1(params)
        elif params.step == S2Query.STEP_2:
            self.step2(params)
            
    def step1(self, params):
        try:
            comments=json.loads(params.content)
            index=len(comments['data']['page']['list'])
        except:
            Logger.getlogging().warning('{0}:40000 No urllist'.format(params.originalurl))
            return
        url=[]
        key = params.customized['key']
        if int(index) > 0:
            totalpage=comments['data']['page']['totalCount']
            page=int(math.ceil(float(totalpage)/self.PAGE_SIZE))
            if page >= self.maxpages:
                page = self.maxpages
            for i in range(1,page+1):
                if i == 1:
                    self.step2(params)
                    continue
                searchurl = S2Query.S2_URL.format(key=key, pagesize=self.PAGE_SIZE, pageno=i)
                url.append(searchurl)
            self.__storeqeuryurllist__(url, S2Query.STEP_2,{'key':key})        

    def step2(self, params):
        jsondata=json.loads(params.content)
        lists = jsondata['data']['page']['list']
        query = Common.urldec(params.customized['key'])
        urllist=[]
        for l in lists:
            title = l['title']
            pubtime = l['releaseDate']
            url = 'http://www.acfun.cn/v/'+l['contentId']
            if self.compareNow(TimeUtility.getuniformtime(pubtime)):
                if self.checktitle(query, title):
                    urllist.append(url)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
        

            
                    
        
        
    
    