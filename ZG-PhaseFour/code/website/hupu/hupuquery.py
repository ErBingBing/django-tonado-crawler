# -*- coding: utf-8 -*-
##############################################################################################
# @file：hupuquery.py
# @author：Huborui
# @date：2016/11/29
# @version：Ver0.0.0.100
# @note：虎扑网获取元搜的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/17
# @note:虎扑网站的浏览器url中关键字使用书名号《》编码时不是utf-8,而是gbk;需先解码utf-8再编码成gbk
###############################################################################################
import math
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from  bs4 import BeautifulSoup 
from utility.xpathutil import XPathUtility
from configuration import constant
from utility.timeutility import TimeUtility
##############################################################################################
# @class：hupuS2Query
# @author：Huborui
# @date：2016/11/29
# @note：虎扑网获取元搜的类，继承于SiteS2Query类
##############################################################################################
class hupuS2Query(SiteS2Query):
    HUPU_QUERY_TEMPLATE = 'https://my.hupu.com/search?q={q}&type=s_subject&sortby=postdate&page={pn}'
    HUPU_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    HUPU_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Huborui
    # @date：2016/11/29
    # @note：虎扑网元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://my.hupu.com/'

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        info_enc = Common.trydecode(info)
        urls = [hupuS2Query.HUPU_QUERY_TEMPLATE.format(q=info_enc, pn =1)]
        self.__storeqeuryurllist__(urls, self.HUPU_S2QUERY_FIRST_PAGE, {'query': info_enc})
      

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
            # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
            if params.step == hupuS2Query.HUPU_S2QUERY_FIRST_PAGE:
                self.step1(params)
            # 从查询页面中获取视频URL
            elif params.step == hupuS2Query.HUPU_S2QUERY_EACH_PAGE: 
                self.step2(params)            
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self, params):
        # 获得首页url参数
        info = params.customized['query']
        xparser = XPathUtility(params.content)
        if not xparser.xpath('//*[@class="mytopic topiclisttr"]'):
            Logger.log(params.url, constant.ERRORCODE_WARNNING_NORESULTS)
            return
        pageList = xparser.getcomments('//span[@class="right"]/a')
        if len(pageList) == 1:
            pageTotal = 1
        else:
            pageTotal=pageList[len(pageList)-2]
            
        if int(pageTotal) >= self.maxpages:
            pageTotal = self.maxpages

        # 所有循环列表
        querylist = []

        # 根据总页数，获取query列表
        for page in range(1, int(pageTotal) + 1, 1):
            if page == 1:
                self.step2(params)
                continue
            url = hupuS2Query.HUPU_QUERY_TEMPLATE.format(q=info,pn=page)
            querylist.append(url)
        self.__storeqeuryurllist__(querylist, hupuS2Query.HUPU_S2QUERY_EACH_PAGE, {'query': info})
        
    #----------------------------------------------------------------------
    def  step2(self, params):
        key = params.customized['query']
        query = Common.urldec(key)
        soup = BeautifulSoup(params.content, 'html5lib')
        tbody = soup.select('.search_topic_list > form > table > tbody')
        lis = tbody[-1].select('tr')
        urllist = []
        for li in lis:
            url = li.select_one('.p_title > a').get('href')
            title = li.select_one('.p_title > a').get_text()
            curtime = li.select('td')[3].get_text()
            if TimeUtility.compareNow(TimeUtility.getuniformtime(curtime), self.querylastdays):
                if Common.checktitle(query, title):
                    urllist.append(url)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)          
        