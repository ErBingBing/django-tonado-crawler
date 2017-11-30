# -*- coding: utf-8 -*-
################################################################################################################
# @file: huyaquery.py
# @author: HeDian
# @date:  2016/11/24
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
import math
import datetime
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from configuration.environment.configure import SpiderConfigure
from bs4 import BeautifulSoup
import re
from  utility.gettimeutil import getuniformtime,compareNow


################################################################################################################
# @class：HuyaS2Query
# @author：HeDian
# @date：2016/11/24
# @note：
################################################################################################################
class HuyaS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://v.huya.com/index.php?r=search/index&p={pageno}&order=news&w={key}'
    FIRST_PAGE = 'http://v.huya.com/index.php?r=search/index&order=news&w={key}'
    MAIN_DOMAIN = 'http://v.huya.com'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：HuyaS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        self.fakeoriginalurl = 'http://v.huya.com/'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()
        self.r = RegexUtility()
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().debug("query")
        keyvalue = Common.urlenc(info)

        #Step1：根据key, 拼出下面的url（不能设置一周检索条件）
        # http://v.huya.com/index.php?r=search/index&order=news&w=key的urlcode
        urls = [HuyaS2Query.FIRST_PAGE.format(key=keyvalue)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == HuyaS2Query.S2QUERY_FIRST_PAGE:
            Logger.getlogging().debug("HuyaS2Query.S2QUERY_FIRST_PAGE")
            #Step2： 根据返回的html,通过xpath://*[@id="tab1"]/div[1]/div/span/em 得到搜索结果总件数
            # 根据总件数，计算出page总数（总件数/20件，除不尽向上取整）拼出搜索结果的url，写文件保存
            soup = BeautifulSoup(params.content,'html5lib')
            if soup.select('.search-no-data-wrap'):
                return
            # 获取不到，则返回
            totalstr = soup.select_one('.search-list > .mod-tab-hd > .act')
            if not totalstr:
                return
            # 获取总检索页数（例如：160）
            totalstr = totalstr.get_text().replace(',','')
            count = int(re.findall('\d+',totalstr)[0])

            # 根据上面的count数，拼出所有的搜索结果url
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            querylist = []
            pagecount = float(count)/self.DEFAULT_PAGE_SIZE
            pages = int(math.ceil(pagecount))
            if pages >= self.maxpages:
                pages = self.maxpages
            for page in range(1, pages + 1, 1):
                url = HuyaS2Query.QUERY_TEMPLATE.format(pageno = page, key = keyvalue)
                Logger.getlogging().debug(url)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, HuyaS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == HuyaS2Query.S2QUERY_EACH_PAGE:
            info = params.customized['query']
            soup = BeautifulSoup(params.content,'html5lib')
            if soup.select('.search-no-data-wrap'):
                return            
            divs = soup.select('ul.video-list')
            if divs:
                divs = divs[-1]
                divs = divs.select('li')
            if not divs:
                return
            
            urllist = []
            for div in divs:
                video = div.select_one('.video-title > .video-wrap')
                timestr = div.select_one('.result-data')
                times = getuniformtime(timestr.get_text())
                titles = video.get('title')
                url = video.get('href')
                if compareNow(times, self.querylastdays) and Common.checktitle(info,titles):
                    Logger.getlogging().debug(titles)
                    Logger.getlogging().debug(url)
                    urllist.append(url)  
                else:
                    Logger.getlogging().debug(titles+' not match title or out of time')
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)

