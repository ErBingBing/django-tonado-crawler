# -*- coding: utf-8 -*-
################################################################################################################
# @file: pptvquery.py
# @author: Merlin.W.ouyang
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: #由于检索结果里面没有视频发布时间这个属性，所以只能标题命中结果之后全部获得了
################################################################################################################
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TIEBA
from bs4 import BeautifulSoup
from configuration import constant
from utility.timeutility import TimeUtility 
################################################################################################################
# @class：cartoonPPTVQuery
# @author：Merlin.W.ouyang
# @date：2016/11/22
# @note：
################################################################################################################
class S2Query(SiteS2Query):
    S2_URL='http://search.pptv.com/result?search_query={key}&search_sort=video_date_uploaded&p={page}#sort'
    STEP_1 = 'Step1'
    STEP_2 = 'Step2'
    STEP_3 = 'Step3'
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：cartoonPPTVQuery，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        self.r = RegexUtility()
        self.fakeoriginalurl='http://cartoon.pptv.com/'
        
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self,info):
        querykey=Common.trydecode(info)
        # step1: 根据key, 拼出下面的url
        query_url = [S2Query.S2_URL.format(key=querykey, page =1)]
        self.__storeqeuryurllist__(query_url, S2Query.STEP_1, {'query':info})
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self,params):
        try:
            if params.step == S2Query.STEP_1:
                self.step1(params)
            elif params.step == S2Query.STEP_2:
                self.step2(params)
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self,params):
        # 搜索页面单个视频
        info = params.customized['query']
        keyvalue = Common.trydecode(info)
        soup = BeautifulSoup(params.content,'html5lib')
        page_numlist = soup.select('#sort > .page > a')
        if soup.select_one('.no-result'):
            Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NORESULTS)
            return                    
        if page_numlist:
            page_num = int(page_numlist[-2].get_text())
        else:
            page_num = 1
        if page_num >= self.maxpages:
            page_num = self.maxpages
        querylist = []
        for page in range(1,page_num+1):
            if page == 1:
                self.step2(params)
                continue
            url = S2Query.S2_URL.format(key=keyvalue, page=page)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, S2Query.STEP_2, {'query': info, 'page_num' : page_num})
   
    #----------------------------------------------------------------------
    def step2(self,params):
        info = params.customized['query']
        query = Common.urldec(info)
        urllist = []
        soup = BeautifulSoup(params.content, 'html5lib')
        items = soup.select('.cf > li > a.ui-list-ct')
        for item in items:
            try:
                url = item.get('href')
                title = item.get('title')
                if self.checktitle(query, title):
                    #urllist.append(url)
                    self.__storeurl__(url, TimeUtility.getuniformdatebefore(0), SPIDER_S2_WEBSITE_VIDEO)  
                else:
                    Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            except:
                Logger.printexception()
        #if len(urllist) > 0:
            #self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
        
            