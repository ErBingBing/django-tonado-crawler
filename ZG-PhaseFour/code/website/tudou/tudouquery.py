# -*- coding: utf-8 -*-
################################################################################################################
# @file: youkuquery.py
# @author: Ninghz
# @date:  2016/11/24
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from lxml import etree
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from  bs4 import BeautifulSoup 
import math

################################################################################################################
# @class：tudouS2Query
# @author：Ninghz
# @date：2016/11/24
# @note：
################################################################################################################
class tudouS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://www.soku.com/nt/search/q_{key}_limitdate_7?site=14&_lg=10&orderby=2'
    QUERY_TEMPLATE2 = 'http://www.soku.com/nt/search/q_{key}_limitdate_7?site=14&orderby=2&_lg=10&page={pageno}'
    
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    limit = 25
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：tudouS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.tudou.com/'
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        # step1: 根据key, 拼出下面的url(最新1周）
        tudouS2Query.QUERY_TEMPLATE = 'http://www.soku.com/nt/search/q_{key}_limitdate_{querydays}?site=14&_lg=10&orderby=2&page={page}'
        keyvalue = Common.urlenc(info)
        urls = [tudouS2Query.QUERY_TEMPLATE.format(key=keyvalue,querydays=self.querylastdays,page=0)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query': keyvalue,'pages_num':0})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == tudouS2Query.S2QUERY_FIRST_PAGE:
            self.step1(params)
        elif params.step == tudouS2Query.S2QUERY_EACH_PAGE:
            self.step2(params)
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        q = params.customized['query']
        pages_num = params.customized['pages_num']
        # 所有循环列表
        soup = BeautifulSoup(params.content,'html5lib')
        if soup.select_one('.sk_null > .sorry') and int(pages_num) == 0:
            Logger.getlogging().warning('{0}:40000 No urllist!'.format(params.url))
            return

        pages = soup.select('.sk_pager > ul > li > a')
        if not pages and int(pages_num) == 0:
            self.step2(params)
            return
        nexted = soup.select_one('.sk_pager > ul > li.next')       
        
        temp = pages_num
        #重新刷新最新页面
        if nexted:
            pages_num = int(pages[-2].get_text())
        elif not soup.select_one('.sk_null > .sorry'):
            pages_num = int(pages[-1].get_text())
            if pages_num <= temp:
                pages_num = temp
        if pages_num >= self.maxpages:
            pages_num = self.maxpages
        querylist = [] 
        
        #第一页最大为10，以后每次最大值为递增5
        maxpage = 10+int(math.ceil(float(pages_num-10)/5))*5 
        if not nexted or pages_num == self.maxpages or (nexted and pages_num < max(pages_num, 10) ):
            for page in range(1,pages_num+1):
                querylist.append(tudouS2Query.QUERY_TEMPLATE.format(key=q, querydays=self.querylastdays, page=page))
            self.__storeqeuryurllist__(querylist, self.S2QUERY_EACH_PAGE, {'query': q})
            return
        querylist.append(tudouS2Query.QUERY_TEMPLATE.format(key=q, querydays=self.querylastdays, page=pages_num))
        self.__storeqeuryurllist__(querylist, self.S2QUERY_FIRST_PAGE, {'query': q,'pages_num':pages_num})        
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        info = params.customized['query']
        soup = BeautifulSoup(params.content,'html5lib')
        if soup.select_one('.sk_null > .sorry'):
            Logger.getlogging().warning('{0}:40000 No urllist!'.format(params.url))
            return        
        html = etree.HTML(params.content)
        hrefs = html.xpath('//*[@class="v-link"]/a/@href')
        titles = html.xpath('//*[@class="v-link"]/a/@title')
        urllist = []
        for index in range(0, len(titles), 1):
            if titles[index]:
                Logger.getlogging().debug(titles[index])
                # match title
                if not Common.checktitle(Common.urldec(info), titles[index]):
                    Logger.getlogging().debug('http:+{url}:40000 checktitle,out of title'.format(url=hrefs[index]))
                    continue
                urllist.append('http:'+hrefs[index])
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)        
        

