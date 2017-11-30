# -*- coding: utf-8 -*-
################################################################################################################
# @file: PK52S2Query.py
# @author: Yongjicao
# @date:  2016/11/29
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
import math
import datetime
import re
import urllib
from configuration import constant 


################################################################################################################
# @class：PK52S2Query
# @author：Yongjicao
# @date：2016/11/29
# @note：
################################################################################################################
class PK52S2Query(SiteS2Query):
    #'http://zhannei.baidu.com/cse/search?q=%E8%A5%BF%E6%A5%9A%E9%9C%B8%E7%8E%8B&p=1&s=10958510337899249915&sti=525600'
    PK52BBS_QUERY_TEMPLATE = 'http://zhannei.baidu.com/cse/search?q={q}&p={p}&s=10958510337899249915&sti={sti}'
    PK52BBS_QUERY_TEMPLATE2 = 'http://zhannei.baidu.com/cse/search?q={q}&s=10958510337899249915&sti={sti}&nsid=0'
    #http://zhannei.baidu.com/cse/search?q=%E5%A4%A7%E8%AF%9D%E8%A5%BF%E6%B8%B8&s=10958510337899249915&stp=1
    DEFAULT_DAY = 365
    DEFAULT_PAGE_SIZE = 10
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    #sti为查询时间天数*1440，默认为365天
    DEFAULT_STI = DEFAULT_DAY*1440
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：PK52S2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://bbs.52pk.com'
        self.r = RegexUtility()

    def getpagecontents(self, params):
        info = params.customized['query']
        # 创建 beautifulsoup 对象
        soup = BeautifulSoup(params.content, 'html.parser')
        # 查找class属性为c-title的h3标记
        results = soup.find_all('h3', 'c-title')
        urllist = []
        if len(results) > 0:
            for result in results:
                # 获取a标记的文本，因search的url中含有sti的参数，这边不考虑时间
                title = (result.find('a').get_text()).strip()
                # if info.decode('utf8') in title.decode('utf8'):
                # if info in title:
                if Common.checktitle(info, title):
                    # 获取a标记的href属性
                    href = result.find('a').get('href')
                    urllist.append(href)
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")

        keyvalue = Common.urlenc(info)

        #keyvalue = info
        # 获取配置文件中的查询天数
        if self.querylastdays == 0:
            sti = self.DEFAULT_STI
        else:
            sti = int(self.querylastdays) * 1440


        urls = [PK52S2Query.PK52BBS_QUERY_TEMPLATE2.format(q = keyvalue,sti = sti)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info,'sti':sti})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == PK52S2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            sti = params.customized['sti']
            keyvalue = Common.urlenc(info)


            html = etree.HTML(params.content)
            totalstr = html.xpath('//*[@id="results"]/span')
            if len(totalstr)>0:
                totalcount = re.sub("\D", "", totalstr[0].text)
            else:
                Logger.getlogging().info('未搜索到与'+info+'相关的数据')
                Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NORESULTS)
                return


            #print totalcount
            # 获取不到，则返回
            if int(totalcount) == 0:
                return

            #获取当前页检索结果
            self.getpagecontents(params)

            # 根据上面的page_count数，拼出除了第一页之外的所有的搜索结果url(最新1周）
            querylist = []
            if totalcount > 0:
                for page in range(2, int(math.ceil(float(totalcount) / self.DEFAULT_PAGE_SIZE)) + 1, 1):
                    if page == 1:
                        url = PK52S2Query.PK52BBS_QUERY_TEMPLATE2.format(q = keyvalue,sti = sti)
                    else:
                        url = PK52S2Query.PK52BBS_QUERY_TEMPLATE.format(q = keyvalue, p = page,sti = sti)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, PK52S2Query.S2QUERY_EACH_PAGE,{'query' : info})

        elif params.step == PK52S2Query.S2QUERY_EACH_PAGE:
            self.getpagecontents(params)
