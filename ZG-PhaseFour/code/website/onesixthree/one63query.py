# -*- coding: utf-8 -*-
################################################################################################################
# @file: one63query.py
# @author: HeDian
# @date:  2016/12/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from lxml import etree
import math

from configuration.environment.configure import SpiderConfigure
from utility.common import Common
from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
import datetime


################################################################################################################
# @class：One63S2Query
# @author：HeDian
# @date：2016/12/22
# @note：
################################################################################################################
class One63S2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://so.v.163.com/search/000-{period}-0000-1-{page}-{order}-{key}/'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    WEEKLY = '2'
    MONTHLY = '3'
    ALL = '0'
    ORDER = '2' #按照发布时间排序


    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：One63S2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://v.163.com/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：getsearchresult
    # @params：输入参数
    # @return：none
    # @note：得到传入的检索结果页面的所有
    ################################################################################################################
    def getsearchresult(self, params):
        info = params.customized['query']

        xpath = XPathUtility(html=params.content)
        hrefs = xpath.xpath('//li/h3/a/@href')
        titles = xpath.getlist('//li/h3/a')
        pubtimes = xpath.xpath('//li/p')

        today = datetime.datetime.strptime(TimeUtility.getcurrentdate(), TimeUtility.DATE_FORMAT_DEFAULT).date()

        urllist = []
        for index in range(0, len(titles), 1):
            # 标题中包含指定要查询的关键字
            # if titles[index].find(info) > -1:
            if Common.checktitle(info, titles[index]):
                pubtimestr = TimeUtility.getuniformdate(pubtimes[index].text)
                pubtime = datetime.datetime.strptime(pubtimestr, TimeUtility.DATE_FORMAT_DEFAULT).date()
                inteveral = today - pubtime
                # 时间在指定周期内
                if inteveral.days <= self.querylastdays:
                    urllist.append(hrefs[index])
                else:
                    # 因为是按照时间排序的，第一条时间不满足检索周期的话，后面所有的都不满足。
                    break

        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        keyvalue = Common.urlenc(info)

        # step1: 根据key, 拼出下面的url
        if self.querylastdays <= 7:
            periodvalue = self.WEEKLY
        elif self.querylastdays <= 30:
            periodvalue = self.MONTHLY
        else:
            periodvalue = self.ALL
        urls = [One63S2Query.QUERY_TEMPLATE.format(period = periodvalue, page = 1, order = self.ORDER, key = keyvalue)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info, 'period':periodvalue})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == One63S2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            periodvalue = params.customized['period']
            keyvalue = Common.urlenc(info)

            # 得到检索结果总件数
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[contains(@class,"result")]/span')
            # 获取不到，则返回
            if len(nodes) == 0:
                return

            # 获取最后一页的页数
            try:
                page_count = int(math.ceil(float(nodes[0].text) / self.DEFAULT_PAGE_SIZE))
            except:
                page_count = 1

            # 获取当前页的检索结果
            self.getsearchresult(params)

            # 根据上面的page_count数，拼出除了首页之外的所有的搜索结果url
            querylist = []
            for page in range(2, page_count + 1, 1):
                url = One63S2Query.QUERY_TEMPLATE.format(period = periodvalue, page = page, order = self.ORDER, key = keyvalue)
                Logger.getlogging().debug(url)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, One63S2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == One63S2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的url，通过xpath获取搜索结果的url，把url写入文件
            self.getsearchresult(params)