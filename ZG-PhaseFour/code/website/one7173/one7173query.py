# -*- coding: utf-8 -*-
##############################################################################################
# @file：V17173S2Query.py
# @author：Liyanrui
# @date：2016/11/23
# @version：Ver0.0.0.100
# @note：17173视频页获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from lxml import etree
import math
import re
import datetime
from utility.regexutil import RegexUtility
from configuration.environment.configure import SpiderConfigure
from  bs4 import  BeautifulSoup
from  log.spiderlog import Logger 
from  utility.gettimeutil import getuniformtime,compareNow
from website.common.bbss2postquery import BBSS2PostQuery 
from  configuration import constant
########################################################################
class One7173Query(SiteS2Query):
    """"""
    #包含get和post请求的不同query
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.post_url = 'http://bbs.17173.com/search.php?mod=forum'
        #self.get_url = 'http://donghua.dmzj.com'
        pass
    
    #----------------------------------------------------------------------
    def  creatobject(self):
        """创建具体的类对象
           !!!注意DmzjS2Query,BBSS2PostQuery类的初始化要有parent参数"""
        self.getQuery = One7173S2Query(self)
        self.postQuery = BBSS2PostQuery(self.post_url,parent=self)
        
    #----------------------------------------------------------------------
    def  query(self,info):
        """分别调用多个query"""
        self.creatobject()
        self.getQuery.query(info)
        self.postQuery.query(info)
        
    #----------------------------------------------------------------------
    def process(self,params):
        """调用具体的取url列表步骤"""
        try:
            if re.search('http[s]{0,1}://v\.17173\.com.*', params.originalurl):
                self.getQuery.process(params)
            if re.search('http[s]{0,1}://bbs\.17173\.com.*', params.originalurl):
                self.postQuery.process(params)
        except:
            Logger.printexception()


##############################################################################################
# @class：V17173S2Query
# @author：Liyanrui
# @date：2016/11/23
# @note：17173视频页获取元搜的类，继承于SiteS2Query类
##############################################################################################
class One7173S2Query(SiteS2Query):
    V17173_QUERY_TEMPLATE = 'http://v.17173.com/so-index.html?key={q}'
    V17173_QUERY_P = 'http://v.17173.com/so-index.html?key={q}&page={ps}&from='
    DEFAULT_PAGE_SIZE = 20
    PAGE = 1
    FIRST = 'first'
    EACH = 'eachquery'
    limit = 30 #本搜索结果最多30页

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/23
    # @note：17173视频页元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self,parent=None):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://v.17173.com/'
        self.r = RegexUtility()
        if parent:
            self.website = parent.website
       

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls = [One7173S2Query.V17173_QUERY_P.format(q=q,ps=0)]
        self.__storeqeuryurllist__(urls, self.FIRST, {'query': q,'pages_num':0})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        q = params.customized['query']
        pages_num = params.customized['pages_num']
        # 所有循环列表
        soup = BeautifulSoup(params.content,'html5lib')
        if soup.select_one('.search-tips') and int(pages_num) == 0:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return
        pages = soup.select('.pagebox > a')
        if not pages and int(pages_num) == 0:
            self.step2(params)
            return
        
        temp = pages_num
        #重新刷新最新页面
        nexted = soup.select_one('.pagebox > .next')
        if nexted:
            pages_num = int(pages[-2].get_text())
        elif not soup.select_one('.search-tips'):
            pages_num = int(pages[-1].get_text())
            if pages_num <= temp:
                pages_num = temp
        if pages_num >= self.maxpages:
            pages_num = self.maxpages
        querylist = []
        #第一页最大为10，以后每次最大值为递增4
        maxpage = 10+int(math.ceil(float(pages_num-10)/4))*4
        if not nexted or pages_num == self.limit or pages_num == self.maxpages or (nexted and pages_num < max(maxpage,10)):
            for page in range(1,pages_num+1):
                querylist.append(One7173S2Query.V17173_QUERY_P.format(q=q,ps=page))
            self.__storeqeuryurllist__(querylist, self.EACH, {'query': q})
            return 
        querylist.append(One7173S2Query.V17173_QUERY_P.format(q=q,ps=pages_num))
        self.__storeqeuryurllist__(querylist, self.FIRST, {'query': q,'pages_num':pages_num})        
        
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        q = params.customized['query']
        soup = BeautifulSoup(params.content,'html5lib')
        divs = soup.select('.videobox')
        if not divs:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return
        urllist = []
        for div in divs:
            title = div.select_one('.title').get_text()
            #print title
            tm = getuniformtime(div.select_one('.date').get_text())
            url = div.select_one('.title > a').get('href')
            Logger.getlogging().debug(title)
            if not compareNow(tm, self.querylastdays):
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
                continue
            if not Common.checktitle(Common.urldec(q), title):
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                continue
            urllist.append(url)
                #获取最终url列表
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)                

    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == self.FIRST:
            self.step1(params)
        if params.step == self.EACH:
            self.step2(params)
