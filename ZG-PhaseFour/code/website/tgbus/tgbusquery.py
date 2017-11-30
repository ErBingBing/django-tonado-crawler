# -*- coding: utf-8 -*-
##############################################################################################
# @file：TGbusS2Query.py
# @author：Yongjicao
# @date：2016/12/01
# @version：Ver0.0.0.100
# @note：电玩巴士论坛获取元搜的文件
###############################################################################################
import math
from configuration import constant
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE, SPIDER_CHANNEL_S1
from utility.common import Common
from website.common.s2query import SiteS2Query
from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility
from log.spiderlog import Logger 
from bs4 import BeautifulSoup 
from utility.timeutility import TimeUtility 
##############################################################################################
# @class：TGbusS2Query
# @author：Yongjicao
# @date：2016/12/01
# @note：电玩巴士论坛获取元搜的类，继承于SiteS2Query类
##############################################################################################
class TGbusS2Query(SiteS2Query):
    #http://bbs.tgbus.com/plugin.php?id=esearch&item=&mymod=search&myac=thread&word=%E5%80%9A%E5%A4%A9%E5%B1%A0%E9%BE%99%E8%AE%B0&srchfilter=all&special=0&srchfrom=31536000&before=0&orderby=_score&ascdesc=desc&accurate=
    #TGBUS_QUERY_TEMPLATE = 'http://bbs.tgbus.com/plugin.php?id=esearch&mymod=search&myac=thread&word={key}&page={pn}&srchfrom={srchfrom}'
    TGBUS_QUERY_TEMPLATE = 'http://bbs.tgbus.com/plugin.php?id=esearch&item=&mymod=search&myac=thread&word={key}&srchfilter=all&special=0&srchfrom={srchfrom}&before=0&orderby=_score&ascdesc=desc&accurate=&page={page}'
    TGBUS_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    TGBUS_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    page_size = 10
    
    DEFAULT_DAY = 365
    DEFAULT_TIME = 86400
    DEFAULT_SRCHFROM = DEFAULT_DAY * DEFAULT_TIME

    

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/12/01
    # @note：电玩巴士论坛元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://bbs.tgbus.com/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        urlkey = Common.urlenc(info)
        # 获取配置文件中的查询天数
        if self.querylastdays == 0:
            srchfrom = self.DEFAULT_SRCHFROM
        else:
            srchfrom = int(self.querylastdays) * self.DEFAULT_TIME
        urls = [TGbusS2Query.TGBUS_QUERY_TEMPLATE.format(key=urlkey, page=1, srchfrom=srchfrom)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.TGBUS_S2QUERY_FIRST_PAGE, {'key': urlkey,'srchfrom':srchfrom})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
            # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
            if params.step == TGbusS2Query.TGBUS_S2QUERY_FIRST_PAGE:
                self.step1(params)
            # 从查询页面中获取视频URL
            elif params.step == TGbusS2Query.TGBUS_S2QUERY_EACH_PAGE:
                self.step2(params)
        except:
            Logger.printexception()

    #----------------------------------------------------------------------
    def step1(self, params):
        key = params.customized['key']
        srchfrom = params.customized['srchfrom']        
        xpath = XPathUtility(params.content)
        text = xpath.getstring('//*[@id="main"]/span')
        tstr = u'搜索总条数'
        if not self.r.search(tstr, text):
            Logger
            return 
        num = self.r.parse('\d+', text)[0]
        pages = int(math.ceil(float(num)/self.page_size))
        if pages >= self.maxpages:
            pages = self.maxpages
        querylist = []
        for page in range(1, pages + 1):
            if page == 1:
                self.step2(params)
                continue
            url = TGbusS2Query.TGBUS_QUERY_TEMPLATE.format(key=key, page=page, srchfrom=srchfrom)
            querylist.append(url) 
        if querylist:
            self.__storeqeuryurllist__(querylist, TGbusS2Query.TGBUS_S2QUERY_EACH_PAGE, {'key': key})
        
    #----------------------------------------------------------------------
    def step2(self, params):
        key = params.customized['key']
        query = Common.urldec(key)
        soup = BeautifulSoup(params.content, 'html5lib')
        lis = soup.select('.sresult > ul > li')
        urllist = []
        for li in lis:
            url = li.select_one('.stitle > a').get('href')
            title = li.select_one('.stitle').get_text()
            curtime = li.select_one('.scontent').get_text()
            if TimeUtility.compareNow(TimeUtility.getuniformtime(curtime), self.querylastdays):
                if Common.checktitle(query, title):
                    urllist.append('http://bbs.tgbus.com/'+url)
                else:
                    Logger.log('http://bbs.tgbus.com/'+url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log('http://bbs.tgbus.com/'+url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)        
                