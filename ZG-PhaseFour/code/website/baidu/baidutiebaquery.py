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
from bs4 import BeautifulSoup
import re
import time
from lxml import etree
from utility import gettimeutil
from configuration import constant
################################################################################################################
# @class：BaiduTiebaS2Query
# @author：Hedian
# @date：2016/12/02
# @note：
################################################################################################################
class BaiduTiebaS2Query(SiteS2Query):

    # 百度贴吧搜索需要的类变量
    TIEBA_QUERY_TEMPLATE = 'https://tieba.baidu.com/f?kw={key}&ie=utf-8&pn={page}'
    BAIDU_TIEBA_SEARCH_FIRST_PAGE = 'BAIDU_TIEBA_SEARCH_FIRST_PAGE'
    BAIDU_TIEBA_SEARCH_EACH_PAGE = 'BAIDU_TIEBA_SEARCH_EACH_PAGE'
    DEFAULT_MAX_PAGESIZE = 50
    MAIN_DOMAIN = 'http://tieba.baidu.com'
    DEFAULT_MAX_PAGE = 50

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：BaiduTiebaS2Query，初始化内部变量
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
        #1.仅贴吧的url搜索贴吧
        if re.search('^http[s]{0,1}:.*',info):
            TIEBA_URL_PATTERN = constant.TIEBA_URL_PATTERN12
            if not re.search(TIEBA_URL_PATTERN,info):
                return
            urls = [info]
            self.__storeqeuryurllist__(urls, self.BAIDU_TIEBA_SEARCH_FIRST_PAGE)
        #else:
            ##仅关键词搜索贴吧
            #keyvalue = Common.urlenc(info)
            #urls = [BaiduTiebaS2Query.TIEBA_QUERY_TEMPLATE.format(key=keyvalue, page=0)]
            #Logger.getlogging().debug(urls[0])
            #self.__storeqeuryurllist__(urls, self.BAIDU_TIEBA_SEARCH_FIRST_PAGE)            


    ################################################################################################################
    # @functions：baidutiebasearch_step2
    # @params： 下载平台传回的下载结果等信息
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def baidutiebasearch_step2(self, params):
        # Step2: 根据返回内容，通过xpath: //*[@class="nums"] 得到最大总条数
        #info = params.customized['query']
        #keyvalue = Common.urlenc(info)
        content = ''
        p = '<!--[\s\S]{0,}(<ul id="thread_list".*[\s\S]{0,})--></code><script>'
        if re.search(p,params.content):
            content = re.findall(p,params.content)[0]
        if not content:
            Logger.log(params.url, constant.ERRORCODE_WARNNING_NORESULTS)
            return 
        # 获取第一页的搜索结果
        self.baidutiebasearch_step3(params)        
        
        soup = BeautifulSoup(content, 'html5lib')
        queryurl = ''
        if soup.select('#thread_list'):
            try:
                if soup.select('#frs_list_pager'):
                    last = soup.select_one('#frs_list_pager > .last').get('href')
                    lists = last.split('pn=')
                    num = lists[1]
                    queryurl = 'https:'+lists[0]
                    tailpage = int(num)/BaiduTiebaS2Query.DEFAULT_MAX_PAGESIZE + 1
                else:
                    tailpage = 1             
            except:
                tailpage = 1
        else:
            # 没有检索结果，直接返回
            Logger.log(params.url, constant.ERRORCODE_WARNNING_NORESULTS)
            return
        if tailpage > BaiduTiebaS2Query.DEFAULT_MAX_PAGE:
            tailpage = BaiduTiebaS2Query.DEFAULT_MAX_PAGE
        if tailpage >= self.maxpages:
            tailpage = self.maxpages
        # 根据上面的tailpage数，拼出除了第一页之外的所有的搜索结果url
        querylist = []
        if not queryurl:
            return
        for page in range(2, tailpage + 1, 1):
            url = queryurl + 'pn={page}'.format(page=(page-1)*BaiduTiebaS2Query.DEFAULT_MAX_PAGESIZE)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, BaiduTiebaS2Query.BAIDU_TIEBA_SEARCH_EACH_PAGE)

    ################################################################################################################
    # @functions：baidutiebasearch_step3
    # @params： 获取每页的具体信息
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def baidutiebasearch_step3(self, params):
        content = ''
        p = '<!--[\s\S]{0,}(<ul id="thread_list".*[\s\S]{0,})--></code><script>'
        if re.search(p,params.content):
            content = re.findall(p,params.content)[0]
        if not content:
            Logger.log(params.url, constant.ERRORCODE_WARNNING_NORESULTS)
            return        
        soup = BeautifulSoup(content, 'html5lib')
        #print soup
        top_list = soup.select('#thread_top_list > li.j_thread_list')
        thread_list = soup.select('#thread_list > li.j_thread_list')
        urllist = []
        for item in top_list+thread_list:
            #print item
            try:
                pubtimeobj = item.find(attrs={'class':'threadlist_reply_date pull_right j_reply_data'})
                if not pubtimeobj:
                    pubtimeobj = item.find(attrs={'class':'pull-right is_show_create_time'})
                pubtime = pubtimeobj.get_text().strip().replace(' ','')
                href = item.select_one('.threadlist_title > a').get('href')
                title = item.select_one('.threadlist_title > a').get('title')
                Logger.getlogging().debug(title)
                Logger.getlogging().debug(pubtime)
                pubtime = self.getuniformtime(pubtime)
                Logger.getlogging().debug(pubtime)
                if self.isyestoday(pubtime):
                    pubtime2obj = item.find(attrs={'class':'pull-right is_show_create_time'})
                    if pubtime2obj:
                        pubtime2= self.getuniformtime(pubtime2obj.get_text())
                        if not gettimeutil.compareNow(pubtime2,self.querylastdays):
                            continue
                    Logger.getlogging().debug('https://tieba.baidu.com'+href)
                    urllist.append('https://tieba.baidu.com'+href) 
            except:
                Logger.printexception()
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
            
    @staticmethod
    def isyestoday(times):
        if isinstance(times,str) or isinstance(times,unicode):
            times = time.mktime(time.strptime(times, "%Y-%m-%d %H:%M:%S"))
        now = time.time() - time.timezone
        cha = 60*60*24*1
        midnight = now - (now % cha) + time.timezone
        premidnight =midnight- cha
        if int(times) >= premidnight and int(times) < midnight:
            return True
        return False
        #return True   
    @staticmethod
    def getuniformtime(times):
        p1 = '(\d+)-(\d+)'
        p2 = '(\d)+:(\d+)'
        new = ''
        if re.search(p1,times):
            if len(times) > 5:
                Logger.getlogging().warning('Please see the time format :{tm}'.format(tm=times))
                return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-365*24*60*60))
            new = str(time.localtime()[0]) + '-' + times + ' 08:00:00'
        elif re.search(p2,times):
            new = str(time.localtime()[0])+'-'+str(time.localtime()[1])+'-'+str(time.localtime()[2])+' '+ times+':00'
        if not new:
            Logger.getlogging().warning('Please see the time format :{tm}'.format(times))
            return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-365*24*60*60))
        return new
