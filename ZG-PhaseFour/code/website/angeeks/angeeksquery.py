# -*- coding: utf-8 -*-
################################################################################################################
# @file: angeeksquery.py
# @author: HeDian
# @date:  2016/12/02
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from lxml import etree
import math
from configuration import constant 
from configuration.environment.configure import SpiderConfigure
from utility.common import Common
from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup 
import datetime


################################################################################################################
# @class：AngeeksS2Query
# @author：HeDian
# @date：2016/12/02
# @note：
################################################################################################################
class AngeeksS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://search.angeeks.com/cse/search?q={key}&p={page}&s=2200009525944885011&srt=cse_createTime&stp=1&sti={date}&nsid=0'
    QUERY_TEMPLATE_ALL = 'http://search.angeeks.com/cse/search?q={key}&p={page}&s=2200009525944885011&srt=cse_createTime&stp=1&nsid=0'
    LINK = 'http://bbs.angeeks.com/thread-{tid}-1-1.html'
    DEFAULT_PAGE_SIZE = 10
    DEFAULT_MAX_PAGE = 75
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    WEEKLY = '10080'
    MONTHLY = '43200'
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
        self.fakeoriginalurl = 'http://bbs.angeeks.com/'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：getfirstpageurl
    # @param：url 检索结果的url
    # @info： 获取输入url的主贴url
    # @return：None或者http://bbs.angeeks.com/thread-4031721-1-1.html
    # @note：对检索的url进行重定位
    ################################################################################################################
    def getfirstpageurl(self, tid):
        newurl = None
        if tid not in self.tids:
            self.tids.append(tid)
            newurl = self.LINK.format(tid=tid)
        return newurl

    ################################################################################################################
    # @functions：preprocess
    # @param：url 检索结果的url
    # @info： 对检索的url进行重定位
    # @return：None或者http://bbs.angeeks.com/thread-4031721-1-1.html
    # @note：对检索的url进行重定位
    ################################################################################################################
    def preprocess(self, url):
        if self.r.search('http://bbs.angeeks.com/thread-\d+-\d+-\d+.html', url):
            # 如果不是论坛主贴，获取tid，拼出主贴url, 返回主贴url
            tid = self.r.parse('http://bbs.angeeks.com/thread-(\d+)-\d+-\d+.html', url)[0]
            newurl = self.getfirstpageurl(tid)
        elif self.r.search('tid=\d+', url):
            # 如果不是论坛主贴，获取tid，拼出主贴url, 返回主贴url
            tid = self.r.parse('tid=(\d+)', url)[0]
            newurl = self.getfirstpageurl(tid)
        else:
            newurl = url
        return newurl

    ################################################################################################################
    # @functions：getpagecomments
    # @param： 来自共通模传入的参数
    # @return：none
    # @note：获取具体检索页面的标题，链接和时间
    ################################################################################################################
    def step_last(self, params):
        urllist = []
        info = params.customized['query']
        soup = BeautifulSoup(params.content, 'html5lib')
        divs = soup.select('#results > .result')
        for div in divs:
            publish = div.select_one('.c-summary-1').get_text()
            title = div.select_one('h3 > a').get_text().strip()
            url = div.select_one('h3 > a').get('href').strip()
            #url = self.preprocess(href)
            if TimeUtility.compareNow(TimeUtility.getuniformtime(publish), self.querylastdays):
                if Common.checktitle(Common.trydecode(info), Common.trydecode(title)):
                    urllist.append(url)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)                
                

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("AngeeksS2Query.query")
        keyvalue = Common.urlenc(info)

        # step1: 根据key, 拼出下面的url
        if int(self.querylastdays) <= 7:
            datevalue = self.WEEKLY
        elif int(self.querylastdays) <= 30:
            datevalue = self.MONTHLY
        else:
            datevalue = None

        if datevalue is None:
            urls = [AngeeksS2Query.QUERY_TEMPLATE_ALL.format(key=keyvalue, page=0)]
        else:
            urls = [AngeeksS2Query.QUERY_TEMPLATE.format(key = keyvalue, page=0, date = datevalue)]

        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info, 'date':datevalue})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == AngeeksS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            datevalue = params.customized['date']
            keyvalue = Common.urlenc(info)

            # 得到检索总件数
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[@id="results"]/span')
            # 获取不到，则返回
            if len(nodes) == 0:
                return

            # 删除检索结果的逗号
            searchcountstr = nodes[0].text.replace(',','')

            # 获取总件数
            searchcount = 0
            if self.r.search(u'\d+', searchcountstr):
                searchcount = int(self.r.parse(u'(\d+)', searchcountstr)[0])

            # 获取最大页数，如果页数超过该网站最大支持页数，设置为最大页数
            page_count = int(math.ceil(float(searchcount) / self.DEFAULT_PAGE_SIZE))
            if page_count > self.DEFAULT_MAX_PAGE:
                page_count = self.DEFAULT_MAX_PAGE
            if page_count >= self.maxpages:
                page_count = self.maxpages

            # 根据上面的page_count数，拼出除了首页之外的所有的搜索结果url
            # page范围：1-74（2页-- 75页）
            querylist = []
            for page in range(0, page_count):
                if page == 0:
                    self.step_last(params)
                    continue
                if datevalue is not None:
                    url = AngeeksS2Query.QUERY_TEMPLATE.format(key = keyvalue, page = page, date = datevalue)
                else:
                    url = AngeeksS2Query.QUERY_TEMPLATE_ALL.format(key = keyvalue, page = page)
                Logger.getlogging().debug(url)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, AngeeksS2Query.S2QUERY_EACH_PAGE, {'query':info, 'date':datevalue})

        elif params.step == AngeeksS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的url，通过xpath获取搜索结果的url，把url写入文件
            self.step_last(params)