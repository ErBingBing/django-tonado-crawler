# -*- coding: utf-8 -*-
################################################################################################################
# @file: ifengquery.py
# @author: HuBorui
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note:
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.common import Common
from configuration import constant
from utility.xpathutil import XPathUtility
from website.common.s2query import SiteS2Query
from utility.regexutil import RegexUtility
from utility.gettimeutil import getuniformtime,compareNow
from lxml import etree
import re
import math
import datetime
from  bs4 import BeautifulSoup 
from utility.timeutility import TimeUtility 
from log.spiderlog import Logger 
################################################################################################################
# @class：ifengquery.py
# @author: HuBorui
# @date:  2016/11/22
# @note：
################################################################################################################
class IfengS2Query(SiteS2Query):
    IFENG_QUERY_TEMPLATE = 'http://so.v.ifeng.com/video?&p={pn}&q={q}'
    DEFAULT_PAGE_SIZE = 22
    IFENG_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    IFENG_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：IfengS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://v.ifeng.com/'


    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls = [IfengS2Query.IFENG_QUERY_TEMPLATE.format(pn = 1,q = q)]
        self.__storeqeuryurllist__(urls, IfengS2Query.IFENG_S2QUERY_FIRST_PAGE, {'query':q})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == IfengS2Query.IFENG_S2QUERY_FIRST_PAGE:
            q = params.customized['query']
            # html = etree.HTML(params.content)
            xparser = XPathUtility(params.content)
            mid_count = xparser.getnumber('//div[@class="serpinfo"]/span/em')
            count = str(mid_count).strip()
            querylist = []
            # 获取不到，则返回
            if count == 0:
                return
            elif count > 0:
                pagenum = int(math.ceil(float(count) / IfengS2Query.DEFAULT_PAGE_SIZE))
                if pagenum >= self.maxpages:
                    pagenum = self.maxpages
                for page in range(1, pagenum + 1, 1):
                    url = IfengS2Query.IFENG_QUERY_TEMPLATE.format(pn = page,q = q)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, IfengS2Query.IFENG_S2QUERY_EACH_PAGE,{'info':q})
        elif params.step == IfengS2Query.IFENG_S2QUERY_EACH_PAGE:
            self.step2(params)
 
 
    def step2(self, params):
        info = Common.urldec(params.customized['info'])
        soup = BeautifulSoup(params.content,'html5lib')
        text_divs = soup.select('.s_r_txt')
        urllist = []
        
        if text_divs:
            for item in text_divs:
                title = item.select_one('h3 > a').get_text()
                url = item.select_one('h3 > a').get('href')
                curtime = item.select('p')[-1].get_text().strip()
                try:
                    if TimeUtility.compareNow(TimeUtility.getuniformtime(curtime), self.querylastdays):
                        if Common.checktitle(info, title):
                            urllist.append(url)
                        else:
                            Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                    else:
                        Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
                except:
                    urllist.append(url)
                self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_VIDEO)
                
           
                        
                    