# -*- coding: utf-8 -*-
################################################################################################################
# @file: ku6query.py
# @author: Yongjicao
# @date:  2016/11/25
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from lxml import etree
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.gettimeutil import getuniformtime,compareNow 
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
import math
import datetime
import re


################################################################################################################
# @class：Ku6S2Query
# @author：Yongjicao
# @date：2016/11/25
# @note：
################################################################################################################
class Ku6S2Query(SiteS2Query):
    #KU6_QUERY_TEMPLATE = 'http://so.ku6.com/search?q={q}&sort=uploadtime&start={start}'
    KU6_QUERY_TEMPLATE = 'http://so.ku6.com/search?q={q}&start={start}&status=list'
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGES = 100 # 根据调查，本网站检索结果最大支持2000条数据（100页）
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：Ku6S2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://comic.ku6.com'
        self.r = RegexUtility()

    ##############################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        keyvalue = Common.urlenc(info)
        #keyvalue = info
        # step1: 根据key, 拼出下面的url
        urls = [Ku6S2Query.KU6_QUERY_TEMPLATE.format(q = keyvalue, start = 1)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        self.newprocess(params)
        # if params.step == Ku6S2Query.S2QUERY_FIRST_PAGE:
        #     self.oldprocess(params)
        #
        # elif params.step == Ku6S2Query.S2QUERY_EACH_PAGE:
        #     # Step3: 根据Step2的url，通过xpath://*[@class="result_title"]/a/@href 获取搜索结果的url，把url写入文件
        #     self.oldprocess(params)
        #
        # else:
        #     pass


    ################################################################################################################
    # @functions：getsearchresult
    # @params： see WebSite.process
    # @return：满足标题和时间要求的url数
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def getsearchresult(self, params):
        info = params.customized['query']
        soup = BeautifulSoup(params.content, 'html5lib')
        lis = soup.select('ul.ckl_cktpp > li.cfix')
        urllist = []
        if lis:
            for li in lis:
                title = li.select_one('h3').get_text()
                # if info not in title:
                if not Common.checktitle(info, title):
                    continue
                times = li.select('p')[-2].get_text()
                times = getuniformtime(times)
                url = li.select_one('h3 > a').get('href')
                if compareNow(times, self.querylastdays):
                    urllist.append(url)
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)

            return len(urllist)
        else:
            return -1



    ################################################################################################################
    # @functions：oldprocess
    # @params： see WebSite.process
    # @return：none
    # @note：根据返回的实际情况，拼出获取返回结果的url
    ################################################################################################################
    def oldprocess(self, params):
        # Step2:
        cur_page_reg = self.r.parse('start=(\d+)', params.url)
        if cur_page_reg:
            cur_page = cur_page_reg[0]

        if int(cur_page) > 1:
            prelastpage = params.customized['prelastpage']
            if int(cur_page) < int(prelastpage):
                # 获取检索结果
                self.getsearchresult(params)
                return

        info = params.customized['query']
        keyvalue = Common.urlenc(info)
        xhtml = etree.HTML(params.content)
        pages = xhtml.xpath('//*[@class="ckl_pag"]/a/text()')
        querylist = []

        # 获取检索结果
        self.getsearchresult(params)

        if len(pages) > 0:
            lastpage_reg = self.r.parse('(\d+)', pages[-1])
            if lastpage_reg:
                lastpage = lastpage_reg[0]
            else:
                lastpage = pages[-2]


            if int(cur_page) == 1 or int(cur_page) == int(prelastpage):
                # 拼出首页之外能看到的检索页a数的url
                start = int(cur_page) + 1
                if self.maxpages > self.MAX_PAGES:
                    self.maxpages = self.MAX_PAGES
                if int(lastpage) > self.maxpages:
                    return
                for page in range(start, int(lastpage) + 1, 1):
                    url = Ku6S2Query.KU6_QUERY_TEMPLATE.format(q=keyvalue, start=page)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, Ku6S2Query.S2QUERY_EACH_PAGE, {'query': info, 'prelastpage':lastpage})

    ################################################################################################################
    # @functions：newprocess
    # @params： see WebSite.process
    # @return：none
    # @note：超过7页，一次拼出50页的url，第二次拼出最大值数的url
    ################################################################################################################
    def newprocess(self, params):
        # Step2:
        cur_page_reg = self.r.parse('start=(\d+)', params.url)
        if cur_page_reg:
            cur_page = cur_page_reg[0]

        if int(cur_page) > 1:
            prelastpage = params.customized['prelastpage']
            if int(cur_page) < int(prelastpage):
                # 获取检索结果
                self.getsearchresult(params)
                return

        # 获取检索结果
        ret = self.getsearchresult(params)
        if ret == -1:
            return

        info = params.customized['query']
        keyvalue = Common.urlenc(info)
        xhtml = etree.HTML(params.content)
        pages = xhtml.xpath('//*[@class="ckl_pag"]/a/text()')
        if len(pages) > 0:
            lastpage_reg = self.r.parse('(\d+)', pages[-1])
            if lastpage_reg:
                lastpage = lastpage_reg[0]
            else:
                lastpage = pages[-2]

            start = int(cur_page) + 1
            if self.maxpages > self.MAX_PAGES:
                self.maxpages = self.MAX_PAGES
            if int(lastpage) > self.maxpages:
                lastpage = self.maxpages

            querylist = []
            if int(cur_page) == 1:
                # 拼出首页之外能看到的检索页数的url
                if int(lastpage) >= 7:
                    lastpage = 50

                for page in range(start, int(lastpage) + 1, 1):
                    url = Ku6S2Query.KU6_QUERY_TEMPLATE.format(q=keyvalue, start=page)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, Ku6S2Query.S2QUERY_EACH_PAGE, {'query': info, 'prelastpage':lastpage})

            elif int(cur_page) == 50:
                for page in range(start, self.maxpages + 1, 1):
                    url = Ku6S2Query.KU6_QUERY_TEMPLATE.format(q=keyvalue, start=page)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, Ku6S2Query.S2QUERY_EACH_PAGE, {'query': info, 'prelastpage':self.maxpages})


