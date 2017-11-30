# -*- coding: utf-8 -*-
################################################################################################################
# @file: renren001query.py
# @author: Merlin.W.ouyang
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/01/13
# @note:129-147行被注释掉的代码没做标题命中,107-126为修改后的代码，添加了标题命中功能
###############################################################################################################
import datetime

from utility.xpathutil import XPathUtility
from lxml import etree 
from bs4 import BeautifulSoup 
from configuration.environment.configure import SpiderConfigure
from utility.common import Common
from website.common.s2query import SiteS2Query
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.gettimeutil import compareNow,getuniformtime 
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA,SPIDER_S2_WEBSITE_QUERY
import re
import math
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE

################################################################################################################
# @class：cartoonPPTVQuery
# @author：Merlin.W.ouyang
# @date：2016/11/22
# @note：
################################################################################################################
########################################################################
class  S2Query(SiteS2Query):
    #S2_URL='http://search.acfun.tv/search?cd=1&type=2&q=%s&sortType=-1\
    #&field=title&sortField=releaseDate&pageNo=%spageSize=10&aiCount=3&spCount=3&isWeb=1&sys_name=pc'
    S2_URL='http://www.renren001.cc/search.asp?page=%s&searchword=%s&s='
    STEP_1 = 11
    STEP_2 = 12 
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：cartoonPPTVQuery，初始化内部变量
    ################################################################################################################
    #----------------------------------------------------------------------
    def __init__(self):
        SiteS2Query.__init__(self)
        self.r = RegexUtility()
        self.fakeoriginalurl='http://www.renren001.cc/search/serach'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()
        
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################        
    #----------------------------------------------------------------------
    def query(self,info):
        Logger.getlogging().info("query")
        querykey=Common.urlenc(Common.trydecode(info).encode('gbk'))
        #querykey = Common.urlenc(info)
        query_url = [S2Query.S2_URL % ('1',querykey)]
        Logger.getlogging().debug(query_url[0])
        self.__storeqeuryurllist__(query_url, self.STEP_1, 
                                   {'key':querykey})
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    #----------------------------------------------------------------------
    def  process(self,params):
        if params.step == S2Query.STEP_1:
            html=etree.HTML(params.content)
            #try:
                #quit=html.xpath['//div[@id="results"]/text()']
                #totalpage='0'
            #except:
                #totalpage=html.xpath('//div[@class="page"]/span/text()')[0]
                #totalpage= totalpage.split("/")[-1]
                #totalpage=re.sub("\D", "",totalpage)
            results = html.xpath('//*[@id="results"]')
            if not results:
                return
            totalpage=html.xpath('//*[@id="div_3"]/*[@class="page"]/span/text()')
            if totalpage:
                totalpage = self.r.parse('(\d+)',totalpage[0].split('/')[-1])[0]
            else:
                Logger.getlogging().info("there are no results you want!")
                return
                
            urllist=[]
            if int(totalpage) >= self.maxpages:
                totalpage = self.maxpages
            if totalpage <>'0':
                for pages in range(0,int(totalpage)):
                    searchurl = S2Query.S2_URL % (pages+1,params.customized['key'])
                    urllist.append(searchurl)
                    self.__storeqeuryurllist__(urllist, S2Query.STEP_2,{'key':params.customized['key']})
            else:
                return
        elif params.step == S2Query.STEP_2:
            comquerkey=Common.urldec(params.customized['key']).decode('gbk').encode('utf-8')
            soup = BeautifulSoup(params.content,'html5lib')
            urllist = []
            divs = soup.find_all(attrs={'class':'result f s0'})
            if not divs:
                return
            for div in divs:
                title = div.select_one('h3.c-title').get_text()
                title = ''.join(title.strip().split())
                url_tm = div.select_one('.c-showurl').get_text()
                
                tm = getuniformtime(url_tm.split('/')[-1])
                url = 'http://'+'/'.join(url_tm.split('/')[0:-1])
                Logger.getlogging().debug(title)
                #Logger.getlogging().debug(url_tm)
                if not Common.checktitle(comquerkey, title):
                    Logger.getlogging().warning('{url}:40000 out of range, the title!'.format(url=params.originalurl))
                    continue
                if not compareNow(tm, self.querylastdays):
                    Logger.getlogging().warning('{url}:40000 out of range, the time!'.format(url=params.originalurl))
                    continue
                urllist.append(url)
            self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_VIDEO)