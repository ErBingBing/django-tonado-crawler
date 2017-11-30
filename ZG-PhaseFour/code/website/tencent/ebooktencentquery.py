# -*- coding: utf-8 -*-

################################################################################################################
# @file: ebooktencentquery.py
# @author: JiangSiwei
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from utility.common import Common
from website.common.s2query import SiteS2Query
import math
from lxml import etree
from log.spiderlog import Logger
import traceback
from bs4 import BeautifulSoup
import re
from utility.gettimeutil import getuniformtime,compareNow 
from configuration.constant import  SPIDER_S2_WEBSITE_NEWS


################################################################################################################
# @class：EbooktencentQuery
# @author：JiangSiwei
# @date：2016/12/20
# @note：
################################################################################################################

class EbooktencentQuery(SiteS2Query) :
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://ebook.qq.com/'
        self.QUERY_TEMPLATE = 'http://ebook.qq.com/search/index/keyWord/{key}/p/{page}.html'
        self.DEFAULT_PAGE_SIZE = 30  
        self.DEFAULT_PAGES = 10
        self.QUERY = None
        self.FIRST = 'FIRST'
        self.EACH = 'EACH' 
        if parent:
            self.website = parent.website             
            
    def query(self, info):
    
        q = Common.urlenc(info)
        urls = [self.QUERY_TEMPLATE.format(key=q,page=1)]
        self.__storeqeuryurllist__(urls, self.FIRST, {'key':q})            
        
    def  process(self,params):
        """"""
        # 初始化内部子类对象
        if params.step == self.FIRST:
            self.step1(params)
        if params.step == self.EACH:
            self.step2(params)        
    ################################################################################################################
    # @functions：step1_ac
    # @params： params
    # @return：none
    # @note：腾讯，获取url列表  
    ################################################################################################################
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        key = params.customized['key']
        querylist = []   
        for page in range(1, self.DEFAULT_PAGES+1):
            url =self.QUERY_TEMPLATE.format(key=key,page=page)
            
            querylist.append(url)
        if len(querylist) > 0:
            self.__storeqeuryurllist__(querylist, self.EACH,{'key':key})
        else:
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.originalurl))

        
        
    ################################################################################################################
    # @functions：step2_ac
    # @params： params
    # @return：none
    # @note：腾讯动漫，解析每一页面，获取链接 
    ################################################################################################################    
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        try:
            key = params.customized['key']
            key = Common.urldec(key)
            soup = BeautifulSoup(params.content,'lxml')
            books = soup.select('#bookList > dl')
            if books:
                urllist = []
                for book in books:
                    title = book.select_one('h3 > a').get_text()
                    if key not in title:
                        continue
                    url = book.select_one('h3 > a').get('href')
                    url = re.findall('(.*)&sword=.*',url)[0]
                    urllist.append(url)
                self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_NEWS)     
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))  
 
   
########################################################################
class BooktencentQuery(SiteS2Query) :
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://book.qq.com/'
        self.QUERY_TEMPLATE = 'http://book.qq.com/search/index/wd/{key}/type//ps/{page_size}/p/{page}'
        self.DEFAULT_PAGE_SIZE = 30  
        self.QUERY = None
        self.FIRST = 'FIRST'
        self.EACH = 'EACH' 
        if parent:
            self.website = parent.website             
            
    def query(self, info):
    
        q = Common.urlenc(info)
        urls = [self.QUERY_TEMPLATE.format(key=q,page_size=self.DEFAULT_PAGE_SIZE,page=1)]
        self.__storeqeuryurllist__(urls, self.FIRST, {'key':q})            
        
    def  process(self,params):
        """"""
        # 初始化内部子类对象
        if params.step == self.FIRST:
            self.step1(params)
        if params.step == self.EACH:
            self.step2(params)        
    ################################################################################################################
    # @functions：step1_ac
    # @params： params
    # @return：none
    # @note：腾讯动漫，通过xpath获取url列表  
    ################################################################################################################
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        key = params.customized['key']

        soup = BeautifulSoup(params.content,'html5lib')
        
        total = soup.select_one('#search_tips')
        if total:
            #print re.findall('\d+',total.get_text())
            total = int(re.findall('\d+',total.get_text())[0])

        querylist = []
        if total > 0:
            for page in range(1, int(math.ceil(float(total) / self.DEFAULT_PAGE_SIZE)) + 1, 1):
                url =self.QUERY_TEMPLATE.format(key=key,page_size=self.DEFAULT_PAGE_SIZE,page=page)
                querylist.append(url)
            if len(querylist) > 0:
                self.__storeqeuryurllist__(querylist, self.EACH,{'key':key})
        else:
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.originalurl))

        
        
    ################################################################################################################
    # @functions：step2_ac
    # @params： params
    # @return：none
    # @note：腾讯动漫，通过xpath解析每一页面，获取链接 
    ################################################################################################################    
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        try:
            key = params.customized['key']
            key = Common.urldec(key)
            soup = BeautifulSoup(params.content,'html5lib')
            books = soup.select('#searchResult > .book')
            if books:
                urllist = []
                for book in books:
                    title = book.select_one('h3 > a').get_text()
                    if key not in title:
                        continue
                    pubtime = book.select('.w_auth')[-2].get_text()
                    url = book.select_one('h3 > a').get('href')
                    if compareNow(getuniformtime(pubtime), self.querylastdays):
                        urllist.append(url)
                self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_NEWS)     
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))  


        