# -*- coding: utf-8 -*-
from utility.common import Common
from website.common.s2query import SiteS2Query
import math
from lxml import etree
from log.spiderlog import Logger
import traceback
from bs4 import BeautifulSoup
from configuration.constant import SPIDER_S2_WEBSITE_NEWS
########################################################################
class ActencentQuery(SiteS2Query) :
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://ac.qq.com/'
        self.ORIGINAL_QUERY_TEMPLATE = 'https://v.qq.com/x/search/?q={key}'
        self.QUERY_TEMPLATE = 'https://v.qq.com/x/search/?ses={session}&q={key}&filter={ufilter}&cur={page_size}'
        self.AC_QUERY_TEMPLATE = 'http://ac.qq.com/Comic/searchList/search/{key}/page/{page_size}'
        self.QUERY_TEMPLATE_FILTER='sort={0}&pubfilter={1}&duration={2}&tabid={3}'
        self.DEFAULT_PAGE_SIZE = 28    
        
        self.AC_QUERY = None
        self.AC_FIRST = 'AC_FIRST'
        self.AC_EACH = 'AC_EACH' 
        if parent:
            self.website = parent.website             
            
    def query(self, info):
        q = Common.urlenc(info)
        urls1 = [self.AC_QUERY_TEMPLATE.format(key=q,page_size=1)]
        self.__storeqeuryurllist__(urls1, self.AC_FIRST, {'key':q})            
        
    def  process(self,params):
        """"""
        # 初始化内部子类对象
        if params.step == self.AC_FIRST:
            self.step1(params)
        if params.step == self.AC_EACH:
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
        total = soup.find(attrs={'class':"ma mod_of mod_bbd all_total_num"})
        if total:
            total = int(total.get_text())

        querylist = []
        if total > 0:
            for page in range(1, int(math.ceil(float(total) / self.DEFAULT_PAGE_SIZE)) + 1, 1):
                url =self.AC_QUERY_TEMPLATE.format(key=key,page_size=page)
                querylist.append(url)
            if len(querylist) > 0:
                self.__storeqeuryurllist__(querylist, self.AC_EACH,{'key':key})
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
            xhtml = etree.HTML(params.content)
            url = xhtml.xpath('//*[@class="mod_book_cover db"]/@href')
            url = ['http://ac.qq.com'+u for u in url]
            title = xhtml.xpath('//*[@class="mod_book_cover db"]/@title')
            title_url = zip(title,url)
            urllist = []
            for t,u in title_url:
                # if Common.urldec(key) in t:
                if Common.checktitle(Common.urldec(key), t):
                    urllist.append(u)
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_NEWS)              
        except:
            Logger.printexception()
 
   
        