# -*- coding: utf-8 -*-
################################################################################################################
# @file: ptbusquery.py
# @author: HeDian
# @date:  2016/12/01
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from lxml import etree

from configuration.environment.configure import SpiderConfigure
from utility.common import Common
from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.gettimeutil import TimeUtility
import datetime


################################################################################################################
# @class：PtbusS2Query
# @author：HeDian
# @date：2016/12/01
# @note：
################################################################################################################
class PtbusS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://bbs.ptbus.com/plugin.php?id=esearch&item=&mymod=search&myac=thread&word={key}&srchfilter=all&special=0&srchfrom={date}&before=0&orderby=dateline&ascdesc=desc&page={page}'
    LINK = 'http://bbs.ptbus.com/thread-{tid}-1-1.html'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    WEEKLY = '604800'
    MONTHLY = '2592000'
    YEARLY = '31536000'
    tids = []


    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：PtbusS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://bbs.ptbus.com/'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：preprocess
    # @param：url 检索结果的url(http://bbs.ptbus.com/forum.php?mod=viewthread&fid=3343&tid=6807246)
    # @info： 对检索的url进行重定位
    # @return：None或者http://bbs.ptbus.com/thread-tid-1-1.html
    # @note：对检索的url进行重定位
    ################################################################################################################
    def preprocess(self, url):
        if self.r.search('tid=\d+', url):
            tid = self.r.parse('tid=(\d+)', url)[0]
            if len(self.tids) == 0:
                self.tids.append(tid)
                newurl = self.LINK.format(tid=tid)
            else:
                if tid not in self.tids:
                    self.tids.append(tid)
                    newurl = self.LINK.format(tid=tid)
                else:
                    newurl = None
        else:
            newurl = url
        return newurl

    def getpagecomments(self, params):
        info = params.customized['query']

        xpath = XPathUtility(html=params.content)
        hrefs = xpath.xpath('//*[@class="sosResult"]/strong/a/@href')
        titles = xpath.getlist('//*[@class="sosResult"]/strong/a')
        pubtimes = xpath.xpath('//*[@class="sosResult"]/span/cite[3]')

        today = datetime.datetime.strptime(TimeUtility.getcurrentdate(), TimeUtility.DATE_FORMAT_DEFAULT).date()

        urllist = []
        for index in range(0, len(titles), 1):
            # 标题中包含指定要查询的关键字
            # if titles[index].find(info) > -1:
            if Common.checktitle(info, titles[index]):
                pubtimestr = TimeUtility.getuniformtime(pubtimes[index].text).split(' ')[0]
                pubtime = datetime.datetime.strptime(pubtimestr, TimeUtility.DATE_FORMAT_DEFAULT).date()
                # pubtime = datetime.datetime.strptime(pubtimestr, TimeUtility.DATE_FORMAT_DEFAULT)
                inteveral = today - pubtime
                # 时间在指定周期内　
                if inteveral.days <= int(self.querylastdays):
                    newurl = self.preprocess(hrefs[index])
                    if newurl is not None:
                        urllist.append(newurl)

        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("PtbusS2Query.query")
        keyvalue = Common.urlenc(info)

        # step1: 根据key, 拼出下面的url
        if int(self.querylastdays) <= 7:
            datevalue = self.WEEKLY
        elif int(self.querylastdays) <= 30:
            datevalue = self.MONTHLY
        else:
            datevalue = self.YEARLY
        urls = [PtbusS2Query.QUERY_TEMPLATE.format(key = keyvalue, date = datevalue, page = 1)]

        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info, 'date':datevalue})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == PtbusS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            datevalue = params.customized['date']
            keyvalue = Common.urlenc(info)

            # 得到尾页的url
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[@class="page_last"]/@href')
            # 获取不到，则返回
            if len(nodes) == 0:
                return
            # 获取最后一页的页数
            page_count = 1
            if self.r.search(u'page=\d+', nodes[0]):
                page_count = int(self.r.parse(u'page=(\d+)', nodes[0])[0])
            if page_count >= self.maxpages:
                page_count = self.maxpages

            # 获取当前页的检索结果
            self.getpagecomments(params)

            # 根据上面的page_count数，拼出除了首页之外的所有的搜索结果url
            querylist = []
            for page in range(2, page_count + 1, 1):
                url = PtbusS2Query.QUERY_TEMPLATE.format(key = keyvalue, date = datevalue, page = page)
                Logger.getlogging().debug(url)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, PtbusS2Query.S2QUERY_EACH_PAGE, {'query':info, 'date':datevalue})

        elif params.step == PtbusS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的url，通过xpath获取搜索结果的url，把url写入文件
            self.getpagecomments(params)