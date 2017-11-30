# -*- coding: utf-8 -*-
################################################################################################################
# @file: gfanQuery.py
# @author: Merlin.W.ouyang
# @date:  2016/11/29
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
import math
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from utility.xpathutil import XPathUtility 
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from configuration import constant
from bs4 import BeautifulSoup
################################################################################################################
# @class：dm78dmQuery
# @author：Merlin.W.ouyang
# @date：2016/11/26
# @note：
################################################################################################################
########################################################################
class  S2Query(SiteS2Query):
    S2_URL='http://bbs.gfan.com/search?q={query}&t=threads&p={page}&s=lastpost&tm={tm}'
    STEP_1 = 1
    STEP_2 = 2
    WEEKLY = 'week'
    MONTHLY = 'month'
    YEARLY = 'year'
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：AcFunQuery，初始化内部变量
    ################################################################################################################
    #----------------------------------------------------------------------
    def __init__(self):
        SiteS2Query.__init__(self)
        self.fakeoriginalurl='http://bbs.gfan.com.cn/android-8342764-1-1.html'
        self.page_size = 10


    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################        
    #----------------------------------------------------------------------
    def query(self,info):
        query = Common.urlenc(info)
        if int(self.querylastdays) <= 7:
            datevalue = self.WEEKLY
        elif int(self.querylastdays) <= 31:
            datevalue = self.MONTHLY
        else:
            datevalue = self.YEARLY   
        url = S2Query.S2_URL.format(query=query, page=1, tm=datevalue)
        self.__storeqeuryurllist__([url], self.STEP_1, 
                                   {'key':query,
                                    'provid':datevalue,
                                    'info':info})
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    #----------------------------------------------------------------------  
    
    def  process(self, params):
        try:
            if params.step == S2Query.STEP_1:
                self.step1(params)
            elif params.step == S2Query.STEP_2:
                self.step2(params)
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self, params):
        total = XPathUtility(params.content).getnumber('//h2[@class="sitems"]')
        if not total:
            Logger.log(params.url, constant.ERRORCODE_WARNNING_NORESULTS)
            return 
        totalpage=int(math.ceil(float(total)/self.page_size))
        if totalpage >= self.maxpages:
            totalpage = self.maxpages

        urllist=[]
        for index in range(1, totalpage+1):
            if index == 1:
                self.step2(params) 
                continue
            searchurl = S2Query.S2_URL.format(query=params.customized['key'],
                                              page=index,
                                              tm=params.customized['provid'])
            urllist.append(searchurl)
        self.__storeqeuryurllist__(urllist, S2Query.STEP_2, {'key':params.customized['key']})
        
    def step2(self, params):
        query = Common.urldec(params.customized['key'])
        soup = BeautifulSoup(params.content, 'html5lib')
        divs = soup.select_one('#wp').select('.sitem')
        urllist = []
        for div in divs:
            url = div.select_one('h3 > a').get('href')
            title = div.select_one('h3 > a').get_text()
            pubtime = div.select('.link > span')[-1].get_text()
            if self.compareNow(TimeUtility.getuniformtime(pubtime)):
                if self.checktitle(query, title):
                    urllist.append(url)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
            
            