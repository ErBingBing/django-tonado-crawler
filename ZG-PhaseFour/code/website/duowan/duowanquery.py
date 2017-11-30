# -*- coding: utf-8 -*-
################################################################################################################
# @file: duowanquery.py
# @author: Ninghz
# @date:  2016/12/21
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.xpathutil import XPathUtility
from utility.gettimeutil import getuniformtime,compareNow
from bs4 import BeautifulSoup 
import math
import re 
from website.common.bbss2postquery import BBSS2PostQuery 
from configuration import constant 
########################################################################
class DuowanQuery(SiteS2Query):
    """"""
    #包含get和post请求的不同query
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.post_url = 'http://bbs.duowan.com/search.php?mod=forum'
        #self.get_url = 'http://donghua.dmzj.com'
        pass
    
    #----------------------------------------------------------------------
    def  creatobject(self):
        """创建具体的类对象
           !!!注意DmzjS2Query,BBSS2PostQuery类的初始化要有parent参数"""
        self.getQuery = DuowanS2Query(self)
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
            if params.step == DuowanS2Query.S2QUERY_FIRST_PAGE:
                self.getQuery.step1(params)
            if params.step == DuowanS2Query.S2QUERY_EACH_PAGE:
                self.getQuery.step2(params)
            if params.step == BBSS2PostQuery.S2QUERY_FIRST_PAGE:
                self.postQuery.step1(params)
            if params.step == BBSS2PostQuery.S2QUERY_EACH_PAGE:
                self.postQuery.step2(params)    
        except:
            Logger.printexception()

################################################################################################################
# @class：DuowanS2Query
# @author：Ninghz
# @date：2016/12/21
# @note：
################################################################################################################
class DuowanS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://video.duowan.com/index.php?r=search/index&order=news&w={key}&p={pageno}'
    DEFAULT_PAGE_SIZE = 20.0
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：DuowanS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self,parent=None):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.duowan.com/'
        if parent:
            self.website = parent.website

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        # step1: 根据key, 拼出下面的url(最新1周）
        keyvalue = Common.urlenc(info)
        url = DuowanS2Query.QUERY_TEMPLATE.format(key=keyvalue, pageno=1)
        urls = [url]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query': keyvalue})
    
    
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        #Step2: 根据返回内容，通过xpath 得到搜索结果总数
        info = params.customized['query']
        xhtml = XPathUtility(html=params.content)
        video_counts = xhtml.getnumber('//*[@class="act"]/span/em')
        Logger.getlogging().debug(video_counts)
        # 获取不到，则返回
        if video_counts == 0:
            return
        page_count = int(math.ceil(video_counts/ DuowanS2Query.DEFAULT_PAGE_SIZE))
        if page_count >= self.maxpages:
            page_count = self.maxpages        
        # 根据上面的page_count数，拼出所有的搜索结果url
        querylist = []
        for page in range(1, page_count + 1, 1):
            url = DuowanS2Query.QUERY_TEMPLATE.format(key=info, pageno=page)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, DuowanS2Query.S2QUERY_EACH_PAGE, {'query': info})

    def step2(self,params):
        """"""
        info = params.customized['query']
        info = Common.urldec(info)
        soup = BeautifulSoup(params.content,'html5lib')
        videos = soup.select('.uiVideo > .uiVideo__item')
        if videos:
            urllist = []
            for video in videos:
                title = video.select_one('h3 > a').get('title')
                pubtime = video.select('.result__data > span')[-1].get_text()
                url = video.select_one('h3 > a').get('href')                
                # if not info in title:
                if compareNow(getuniformtime(pubtime),self.querylastdays):
                    if Common.checktitle(info, title):
                        urllist.append(url)
                    else:
                        Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
                    
        
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == DuowanS2Query.S2QUERY_FIRST_PAGE:
            self.step1(params)

        elif params.step == DuowanS2Query.S2QUERY_EACH_PAGE:
            self.step2(params)