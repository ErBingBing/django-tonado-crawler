# -*- coding: utf-8 -*-
from utility.common import Common
from website.common.s2query import SiteS2Query
import math
from lxml import etree
from log.spiderlog import Logger
import traceback
from bs4 import BeautifulSoup
import re
from configuration.constant import SPIDER_S2_WEBSITE_NEWS
from utility.gettimeutil import getuniformtime,compareNow

########################################################################
class Newstencent(SiteS2Query):
    #COMMON_URL = 'http://news.sogou.com/news?query=site:qq.com%20{info}&manual=true&mode=2&sort=1&page={page}'
    COMMON_URL = 'http://news.sogou.com/news?query=site%3Aqq.com+{info}&_asf=news.sogou.com&sort=1&mode=2&manual=true&dp=1&page={page}'
    
    NEWS_FIRST= 'news_FIRST'
    NEWS_EACH = 'news_EACH'       
    NEWS_EACH_2 = 'news_EACH_2'
    
    def __init__(self,parent=None):
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://news.sogou.com'        
        self.page_size = 10 
        if parent:
            self.website = parent
        
    def query(self, info):
        info = Common.trydecode(info).encode('gbk')
        q = Common.urlenc(info)
        urls1 = [self.COMMON_URL.format(info=q,page=1)]
        self.__storeqeuryurllist__(urls1, self.NEWS_FIRST, {'info':q, 'pages_num':1}) 
        
    def process(self, params):
        if params.step == Newstencent.NEWS_FIRST:
            self.step1(params)
        elif params.step == Newstencent.NEWS_EACH:
            self.step2(params) 
        elif params.step == Newstencent.NEWS_EACH_2:
            self.step3(params)
    def step1(self, params):
        info = params.customized['info'] 
        pages_num = params.customized['pages_num'] 
        soup = BeautifulSoup(params.content,'html5lib')
        #print soup
        if soup.find(attrs={"id":re.compile('noresult_part._container')}) and int(pages_num) == 1:
            Logger.getlogging().warning('{0}:40000 No urllist!'.format(params.url))
            return
        pages = soup.find_all(attrs={'id':re.compile('sogou_page_.*')})
        if not pages and int(pages_num) == 1:
            self.step2(params)
            return
        nexted = soup.select_one('#sogou_next')
        temp = pages_num
        #重新刷新最新页面
        if nexted:
            pages_num = int(pages[-1].get_text())
        elif not soup.find(attrs={"id":re.compile('noresult_part._container')}):
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
                querylist.append(Newstencent.COMMON_URL.format(info=info, page=page))
            self.__storeqeuryurllist__(querylist, self.NEWS_EACH)
            return
        querylist.append(Newstencent.COMMON_URL.format(info=info, page=pages_num))
        self.__storeqeuryurllist__(querylist, self.NEWS_FIRST, {'info': info,'pages_num':pages_num})     
        
    def step2(self,params):
        soup = BeautifulSoup(params.content, 'html5lib')
        if soup.find(attrs={"id":re.compile('noresult_part._container')}):
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.url))
            return 
        results = soup.select('.results > .vrwrap')
        if not results:
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.url))
            return 
        urllist = []
        newurllist = []
        for item in results:
            try:
                if not item.select_one('h3.vrTitle > a'):
                    continue
                title = item.select_one('h3.vrTitle > a').get_text()
                href = item.select_one('h3.vrTitle > a').get('href')
                timestr = item.select_one('.news-detail > .news-info > .news-from').get_text()
                times = getuniformtime(timestr)
                Logger.getlogging().debug('title:'+ title)
                Logger.getlogging().debug('time:'+ times)
                if compareNow(times, self.querylastdays):
                    Logger.getlogging().debug('href:'+ href)
                    urllist.append(href)
                newitem = item.select_one('#news_similar')
                if newitem:
                    newhref = 'http://news.sogou.com/news'+newitem.get('href')
                    Logger.getlogging().debug('newhref:'+ newhref)
                    newurllist.append(newhref)
            except:
                Logger.printexception()
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_NEWS)      
        if len(newurllist) > 0:
            self.__storeqeuryurllist__(newurllist, self.NEWS_EACH_2)
            
    def step3(self,params):
        soup = BeautifulSoup(params.content, 'html5lib')
        if soup.find(attrs={"id":re.compile('noresult_part._container')}):
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.url))
            return 
        results = soup.select('.results > .vrwrap')
        if not results:
            Logger.getlogging().warning('{url}:40000 No results'.format(url=params.url))
            return 
        urllist = []
        for item in results:
            try:
                if not item.select_one('h3.vrTitle > a'):
                    continue
                if item.select_one('#hint_container'):
                    continue
                title = item.select_one('h3.vrTitle > a').get_text()
                href = item.select_one('h3.vrTitle > a').get('href')
                timestr = item.select_one('.news-detail > .news-info > .news-from').get_text()
                times = getuniformtime(timestr)
                Logger.getlogging().debug('title:'+ title)
                Logger.getlogging().debug('time:'+ times)
                if compareNow(times, self.querylastdays):
                    Logger.getlogging().debug('href:'+ href)
                    urllist.append(href) 
            except:
                Logger.printexception()
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_NEWS)            
        
    