# -*- coding: utf-8 -*-
##############################################################################################
# @file：tian52S2Query.py
# @author：Liyanrui
# @date：2016/11/24
# @version：Ver0.0.0.100
# @note：天上人间动漫网获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from lxml import etree
import datetime
from utility.regexutil import RegexUtility
from configuration.environment.configure import SpiderConfigure
from bs4 import BeautifulSoup 
from log.spiderlog import  Logger
from utility.gettimeutil import getuniformtime,compareNow
import re
##############################################################################################
# @class：tian52S2Query
# @author：Liyanrui
# @date：2016/11/24
# @note：天上人间动漫网获取元搜的类，继承于SiteS2Query类
##############################################################################################
class tian52S2Query(SiteS2Query):
    TIAN52_QUERY_TEMPLATE = 'http://www.52tian.net/-----------/{q}/'
    TIAN52_QUERY_P_TEMPLATE = 'http://www.52tian.net/-----------{p}/{q}/'
    TIAN52_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    TIAN52_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    TIAN52_S2QUERY_EACH_PAGE_CMP = 'S2QUERY_EACH_PAGE_CMP'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/24
    # @note：天上人间动漫网搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.52tian.net/'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls = [tian52S2Query.TIAN52_QUERY_TEMPLATE.format(q=q)]
        self.__storeqeuryurllist__(urls, self.TIAN52_S2QUERY_FIRST_PAGE, {'query': q})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
              
            # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
            if params.step == tian52S2Query.TIAN52_S2QUERY_FIRST_PAGE:
                self.step1(params)
                # 获得首页url参数
            elif params.step == tian52S2Query.TIAN52_S2QUERY_EACH_PAGE:
                #print '########',params.content
                if self.r.search(u'/v7/404.asp',params.content):
                    Logger.getlogging().warning('{url}:40000. HttpRespond:404 Maybe no search results'.format(url = params.url))
                    return                  
                if re.findall('^http[s]{0,1}://www\.52tian\.net/[(qingbao)|(tupian)|(yinyue)].*',params.originalurl):
                    self.step3(params)
                else:
                    self.step2(params)  
                
        except:
            Logger.printexception()

    #----------------------------------------------------------------------
    def step1(self,params):
        """获取查询的url列表"""
        q = params.customized['query']
        soup = BeautifulSoup(params.content,'html5lib')
        pageobj = soup.select('.pages > a')
        if pageobj:
            pages= int(pageobj[-3].get_text())
        else:
            pages = 1
        # 所有循环列表
        querylist = []
        # 根据总页数，获取query列表
        for page in range(1, pages + 1, 1):
            url = tian52S2Query.TIAN52_QUERY_P_TEMPLATE.format(
                p=page,
                q=params.customized['query'])
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, tian52S2Query.TIAN52_S2QUERY_EACH_PAGE, {'query': q})        
        
    #----------------------------------------------------------------------
    def step2(self,params):
        """获取视频类的url列表"""
        key = Common.urldec(params.customized['query'])
        soup = BeautifulSoup(params.content,'html5lib')
        lis = soup.select('.imagelist2 > ul > li')
        if lis:
            urllist = []
            for li in lis:
                title = li.select_one('a').get_text()
                if key not in title:
                    continue
                url = li.select_one('a').get('href')
                urllist.append(url)
            self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_VIDEO)
    #----------------------------------------------------------------------
    #新闻部分暂时没做
    def step3(self,params):
        """获取新闻类的url列表"""
        key = Common.urldec(params.customized['query'])
        soup = BeautifulSoup(params.content,'html5lib')
        lis = soup.select('.wzlist > ul > li.wztitle')
        if lis:
            urllist = []
            for li in lis:
                title = li.select_one('a').get_text()
                # if key not in title:
                if not Common.checktitle(key, title):
                    continue
                pubtime = li.select_one('span').get_text()
                url = 'http://www.52tian.net' + li.select_one('a').get('href')
                if compareNow(getuniformtime(pubtime),self.querylastdays):
                    urllist.append(url)
            self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_VIDEO)        
        # 从查询页面中获取视频URL
        #elif params.step == tian52S2Query.TIAN52_S2QUERY_EACH_PAGE:
        #urllist = []
        ## 获取关键字
        #q = params.customized['query']
        ## 获取文本
        #content = etree.HTML(params.content)
        ## 如果检索内容为空的场合
        #if content.text is None:
        #self.__storeqeuryurllist__(urllist, tian52S2Query.TIAN52_S2QUERY_EACH_PAGE_CMP, {'query': q})
        #else:
        ## 获取该页超级链接
        #hrefs = content.xpath('//*[@class="wrap52tian"]/div/div/ul/li/a/@href')
    
        #for href in hrefs:
        #urllist.append(href)
        #print href
        #self.__storeqeuryurllist__(urllist, tian52S2Query.TIAN52_S2QUERY_EACH_PAGE_CMP, {'query': q})
        
        
        
        

                
