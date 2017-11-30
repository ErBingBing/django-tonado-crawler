# -*- coding: utf-8 -*-
################################################################################################################
# @file: zolbbsquery.py
# @author: Yongjicao
# @date:  2016/11/26
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE
from lxml import etree
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
import math
import datetime
import re
import urllib


################################################################################################################
# @class：zolbbsquery
# @author：Yongjicao
# @date：2016/11/26
# @note：
################################################################################################################
class ZolBbsS2Query(SiteS2Query):
    # http://bbs.zol.com.cn/index.php?c=search&a=&kword=%C6%BB%B9%FB8&order=1&cdate=3&page=2
    ZOLBBS_QUERY_TEMPLATE = 'http://bbs.zol.com.cn/index.php?c=search&a=&kword={kword}&order=1&cdate={cdate}&page={page}'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    DEFAULT_DAY = 365
    MAIN_URL = 'http://bbs.zol.com.cn/'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：ZolBbsS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://bbs.zol.com.cn'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        # 获取配置文件中的查询天数
        if self.querylastdays == 0:
            cdate = self.DEFAULT_DAY
        else:
            cdate = self.querylastdays
        #string = Common.trydecode(info)
        #string = string.encode('gb2312')
        #d = {'name': string}
        #keyvalue = urllib.urlencode(d)[5:]
        keyvalue = Common.urlenc(Common.trydecode(info).encode('gbk'))
        # step1: 根据key, 拼出下面的url(最新1周）
        urls = [ZolBbsS2Query.ZOLBBS_QUERY_TEMPLATE.format(kword = keyvalue,cdate = cdate, page = 1)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':keyvalue,'info':info,'cdate':cdate})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        urllist = []
        if params.step == ZolBbsS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['info']
            keyvalue = params.customized['query']
            cdate = params.customized['cdate']

            #keyvalue = Common.urlenc(info)

            html = etree.HTML(params.content)
            totalstr = html.xpath('//span[@class="search-title"]/text()')
            totalcount = re.sub("\D", "",totalstr[1])
            #print totalcount
            # 获取不到，则返回
            if int(totalcount) == 0:
                return

            # 根据上面的page_count数，拼出所有的搜索结果url(最新1周）
            querylist = []
            if totalcount > 0:
                for page in range(1, int(math.ceil(float(totalcount) / self.DEFAULT_PAGE_SIZE)) + 1, 1):
                    url = ZolBbsS2Query.ZOLBBS_QUERY_TEMPLATE.format(kword = keyvalue,cdate = cdate, page = page)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, ZolBbsS2Query.S2QUERY_EACH_PAGE,{'query' : keyvalue,'info':info})

        elif params.step == ZolBbsS2Query.S2QUERY_EACH_PAGE:
            info = params.customized['info']
            keyvalue = params.customized['query']
            html = etree.HTML(params.content)
            soup = BeautifulSoup(params.content, 'lxml')
            results = soup.find_all('ul', 'results-list')


            for result in results:
                restr = str(result.find('a',''))
                value = self.r.parse('<a href="(.*)" target="_blank" title="(.*)">.*</a>',restr)[0]
                if value:
                    if value[1] is not None:
                        title = value[1].strip()
                        if Common.checktitle(Common.trydecode(info), Common.trydecode(title)):
                            href = value[0]
                            #如果href是以http开始，http://bbs.zol.com.cn/sjbbs/d34130_156664.htm
                            if self.r.parse(r'^http://.*', href):
                                urllist.append(href)
                            #如果href是以/开头，/quanzi/d643_841594.html，则拼上http://bbs.zol.com.cn
                            elif self.r.parse(r'^/.*', href):
                                href = self.MAIN_URL + href
                                urllist.append(href)
                            else:
                                return
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
        #print urllist