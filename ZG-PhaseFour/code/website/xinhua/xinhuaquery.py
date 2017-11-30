# -*- coding: utf-8 -*-
##############################################################################################
# @file：xinhuaS2Query.py
# @author：Liyanrui
# @date：2016/11/26
# @version：Ver0.0.0.100
# @note：新华网获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from lxml import etree
import re
import datetime
from utility.regexutil import RegexUtility
from bs4 import BeautifulSoup
from  utility.gettimeutil  import getuniformtime,compareNow
from  log.spiderlog import Logger 

##############################################################################################
# @class：xinhuaS2Query
# @author：Liyanrui
# @date：2016/11/26
# @note：新华网获取元搜的类，继承于SiteS2Query类
##############################################################################################
class xinhuaS2Query(SiteS2Query):
    XINHUA_QUERY_TEMPLATE = 'http://search.home.news.cn/forumbookSearch.do?sw={q}&srchType=3&pageNo={pn}'
    XINHUA_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    XINHUA_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/26
    # @note：新华网元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://forum.home.news.cn/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        info_enc = Common.trydecode(info)
        urls = [xinhuaS2Query.XINHUA_QUERY_TEMPLATE.format(q=info_enc, pn =1)]
        self.__storeqeuryurllist__(urls, self.XINHUA_S2QUERY_FIRST_PAGE, {'query': info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
            # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
            if params.step == xinhuaS2Query.XINHUA_S2QUERY_FIRST_PAGE:
                self.step1(params)
            # 从查询页面中获取视频URL
            elif params.step == xinhuaS2Query.XINHUA_S2QUERY_EACH_PAGE:
                self.step2(params) 
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        # 获得首页url参数
        info = params.customized['query']
        info_enc = Common.trydecode(info)
        pagenum = int(re.findall('(\d+)', params.content)[0])

        if int(pagenum) == 0:
            return
        if int(pagenum) >= self.maxpages:
            pagenum = self.maxpages

        # 所有循环列表
        querylist = []

        # 根据总页数，获取query列表
        for page in range(1, pagenum + 1, 1):
            if page == 1:
                params.customized['query'] = info
                self.step2(params)
                continue
            url = xinhuaS2Query.XINHUA_QUERY_TEMPLATE.format(
                q=info_enc,
                pn=page)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, xinhuaS2Query.XINHUA_S2QUERY_EACH_PAGE, {'query': info})
        
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        query = params.customized['query']
        soup = BeautifulSoup(params.content, 'html.parser')
        trs = soup.select('#schend')
        if not trs:
            return
        urllist = []
        for tr in trs:
            title = tr.select_one('.sb14b').get_text()
            content = etree.HTML(str(tr)) 
            publicTimes = content.xpath('//*[@id="schend"]/table[1]/tr/td[3]/text()')[-1].strip()
            href = tr.select_one('.sb14b').get('href')
            id = re.findall('id=(\d+)&',href)[0]
            url = 'http://forum.home.news.cn/detail/' + id + '/1.html'
            if not compareNow(getuniformtime(publicTimes), self.querylastdays):
                continue
            if not Common.checktitle(Common.trydecode(query), Common.trydecode(title)):
                continue
            urllist.append(url)
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)        
        