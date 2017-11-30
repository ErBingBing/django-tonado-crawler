# -*- coding: utf-8 -*-
################################################################################################################
# @file: baidutiebaquery.py
# @author: Hedian
# @date:  2016/12/02
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/02/10
# @note:第76-94行,添加了搜索结果只有1页时的处理
# @date:2017/02/13
# @note:第91-92行,对百度贴吧页码超多设置的maxpages时，取maxpages。
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from utility.common import Common
from utility.xpathutil import XPathUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
import datetime
import time
from utility.gettimeutil import getuniformtime 
from bs4 import BeautifulSoup
import re
from configuration import constant
################################################################################################################
# @class：BaiduTiebaS2Query2
# @author：Hedian
# @date：2016/12/02
# @note：
################################################################################################################
class BaiduTiebaS2Query2(SiteS2Query):

    # 百度贴吧搜索需要的类变量
    TIEBA_QUERY_TEMPLATE = 'http://tieba.baidu.com/f/search/res?ie=utf-8&kw=&qw={key}&rn=30&un=&only_thread=1&sm=1&pn={page}'
    BAIDU_TIEBA_SEARCH_FIRST_PAGE = 'BAIDU_TIEBA_SEARCH_FIRST_PAGE2'
    BAIDU_TIEBA_SEARCH_EACH_PAGE = 'BAIDU_TIEBA_SEARCH_EACH_PAGE2'
    DEFAULT_MAX_PAGESIZE = 30
    MAIN_DOMAIN = 'http://tieba.baidu.com'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：BaiduTiebaS2Query2，初始化内部变量
    ################################################################################################################
    def __init__(self, parent):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://tieba.baidu.com'
        self.r = RegexUtility()
        self.website = parent.website

    ################################################################################################################
    # @functions：baidutiebasearch_step1
    # @info： 查询条件
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def baidutiebasearch_step1(self, info):
        if re.search('^http[s]{0,1}:.*',info):
            TIEBA_URL_PATTERN = constant.TIEBA_URL_PATTERN22
            if not re.search(TIEBA_URL_PATTERN,info):
                return
            urls = [info]
            self.__storeqeuryurllist__(urls, self.BAIDU_TIEBA_SEARCH_FIRST_PAGE)
        else:
            keyvalue = Common.urlenc(info)
            urls = [BaiduTiebaS2Query2.TIEBA_QUERY_TEMPLATE.format(key=keyvalue, page=1)]
            self.__storeqeuryurllist__(urls, self.BAIDU_TIEBA_SEARCH_FIRST_PAGE)            

    ################################################################################################################
    # @functions：baidutiebasearch_step2
    # @params： 下载平台传回的下载结果等信息
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def baidutiebasearch_step2(self, params):
        # Step2: 根据返回内容，通过xpath: //*[@class="nums"] 得到最大总条数
        # 获取第一页的搜索结果
        self.baidutiebasearch_step3(params)        
        # 获取尾页page数
        xparser = XPathUtility(html=params.content)
        pager_search = xparser.xpath('//*[@class="pager pager-search"]')
        queryurl = ''
        if pager_search:
            tailpageurl = xparser.xpath('//*[@class="pager pager-search"]/a[last()]/@href')
            try:
                if tailpageurl:
                    lists = tailpageurl[0].split('pn=')
                    queryurl = 'http://tieba.baidu.com'+lists[0]
                    tailpage = int(lists[1])
                    if tailpage > BaiduTiebaS2Query2.DEFAULT_MAX_PAGESIZE:
                        tailpage = BaiduTiebaS2Query2.DEFAULT_MAX_PAGESIZE
                    if tailpage > self.maxpages:
                        tailpage = self.maxpages                
                else:
                    tailpage = 1                
            except:
                tailpage = 1
        else:
            # 没有检索结果，直接返回
            Logger.log(params.url, constant.ERRORCODE_EXCEPTTION_JSON)
            return
        if not queryurl:
            return
        # 根据上面的tailpage数，拼出除了第一页之外的所有的搜索结果url
        querylist = []
        for page in range(2, tailpage + 1, 1):
            url = queryurl + 'pn={page}'.format(page=page)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, BaiduTiebaS2Query2.BAIDU_TIEBA_SEARCH_EACH_PAGE)

    ################################################################################################################
    # @functions：baidutiebasearch_step3
    # @params： 获取每页的具体信息
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def baidutiebasearch_step3(self, params):
        soup = BeautifulSoup(params.content, 'html5lib')
        post_list = soup.select('.s_post_list > .s_post')
        urllist = []
        for item in post_list:
            try:
                title = item.select_one('.p_title > a').get_text().strip()
                href = item.select_one('.p_title > a').get('href') 
                pubtimeobj = item.find(attrs={'class':'p_green p_date'})
                if not pubtimeobj:
                    Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
                    continue
                pubtime = pubtimeobj.get_text()
                pubtime = getuniformtime(pubtime)
                Logger.getlogging().debug(title)
                Logger.getlogging().debug(pubtime)
                if self.isyestoday(pubtime):
                    Logger.getlogging().debug('https://tieba.baidu.com'+href)
                    urllist.append('https://tieba.baidu.com'+href) 
                else:
                    Logger.log(params.url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
            except:
                Logger.printexception()
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)        

    @staticmethod
    def isyestoday(times):
        if isinstance(times,str):
            times = time.mktime(time.strptime(times, "%Y-%m-%d %H:%M:%S"))
        now = time.time() - time.timezone
        cha = 60*60*24*1
        midnight = now - (now % cha) + time.timezone
        premidnight =midnight- cha
        if int(times) >= premidnight and int(times) < midnight:
            return True
        return False
        #return True