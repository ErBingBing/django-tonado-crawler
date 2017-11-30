# -*- coding: utf-8 -*-
################################################################################################################
# @file: kankanquery.py
# @author: Yongjicao
# @date:  2016/11/23
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from lxml import etree
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
import math
import datetime
import re


################################################################################################################
# @class：KanKanQuery
# @author：Yongjicao
# @date：2016/11/23
# @note：
################################################################################################################
class KanKanS2Query(SiteS2Query):
    #KANKAN_QUERY_TEMPLATE = 'http://search.kankan.com/search.php?page={page}&keyword={keyword}'
    KANKAN_QUERY_TEMPLATE = 'http://search.kankan.com/search.php?page={page}&keyword={keyword}&limit={limit}'
    DEFAULT_PAGE_SIZE = 24
    MAX_PAGE_COUNT = 42
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    DEFAULT_LIMIT =30
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：IqiyiS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        self.fakeoriginalurl = 'http://www.kankan.com/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        if self.querylastdays == 0:
            limit = self.DEFAULT_LIMIT
        else:
            limit = self.querylastdays

        keyvalue = Common.urlenc(info)
        #keyvalue = info
        # step1: 根据key, 拼出下面的url(最新1周）
        urls = [KanKanS2Query.KANKAN_QUERY_TEMPLATE.format(keyword = keyvalue, page = 1,limit =limit)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info,'limit' : limit})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == KanKanS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            limit = params.customized['limit']
            html = etree.HTML(params.content)
            if not html.xpath('//*[@id="video_box"]'):
                return 
            nodes = html.xpath('//p[@class="list-pager-v2"]/a[last()-1]')
            # 获取不到，则返回
            if len(nodes) == 0:
                page_count = 1
            else:
                page_count = int(nodes[0].text)
            # 根据上面的page_count数，拼出所有的搜索结果url(最新1周）
            querylist = []
            if page_count > 0:
                for page in range(1, page_count + 1, 1):
                    url = KanKanS2Query.KANKAN_QUERY_TEMPLATE.format(keyword = info, page = page,limit =limit)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, KanKanS2Query.S2QUERY_EACH_PAGE,{'query' : info})

        elif params.step == KanKanS2Query.S2QUERY_EACH_PAGE:
            info = params.customized['query']
            soup = BeautifulSoup(params.content, 'lxml')
            results = soup.find_all('p', 'title')
            urllist = []
            for result in results:
                title = result.find('a').get('title')
                # if info in title:
                if Common.checktitle(info, title):
                    #因search的url中含有limit=7(包含一周)的参数，这边不考虑时间
                    href = result.find('a').get('href')
                    urllist.append(href)
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
