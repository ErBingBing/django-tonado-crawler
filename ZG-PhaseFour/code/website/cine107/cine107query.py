# -*- coding: utf-8 -*-
################################################################################################################
# @file: cine107query.py
# @author: Ninghz
# @date:  2016/12/2
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/01/17
# @note:第122-123行时间过滤和标题命中有误，修改为128-130行代码
################################################################################################################
import math
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from bs4 import BeautifulSoup
from utility.timeutility import TimeUtility
from utility.gettimeutil import getuniformtime,compareNow

################################################################################################################
# @class：Cine107S2Query
# @author：Ninghz
# @date：2016/12/2
# @note：
################################################################################################################
class Cine107S2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://zhannei.baidu.com/cse/search?s=12380302712006797352&q={key}&p={pageno}'
    DEFAULT_PAGE_SIZE = 10.0
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：cine107S2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        self.fakeoriginalurl = 'http://107cine.com/'
        self.r = RegexUtility()
        

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        # step1: 根据key, 拼出下面的url(最新1周）
        keyvalue = Common.urlenc(info)
        urls = [Cine107S2Query.QUERY_TEMPLATE.format(key=keyvalue, pageno=0)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query': keyvalue})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == Cine107S2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，得到搜索结果总数
            info = params.customized['query']
            soup = BeautifulSoup(params.content, 'html5lib')
            # 搜素结果
            #print soup
            results = soup.select('#results')[0]
            # 无查找结果，则返回
            if results.get_text().find('抱歉') > -1:
                return
            else:
                resultStr = results.select('span.support-text-top')[0].get_text().strip()
                resultStr = resultStr[8:resultStr.index('个')]
                if resultStr.find(',') > -1:
                    result_counts = int(resultStr.replace(',', ''))
                else:
                    result_counts = int(resultStr)
                    Logger.getlogging().debug(result_counts)
                #搜索结果只能查看75[0:74]页，如果超过75页，按照75页处理
                if result_counts > 750:
                    result_counts = 750

            #计算出循环页数page_count
            if result_counts < 10:
                page_count = 0
            else:
                page_count = int(math.ceil(result_counts / Cine107S2Query.DEFAULT_PAGE_SIZE))
            # 根据上面的page_count数，拼出所有的搜索结果url
            querylist = []
            for page in range(0, page_count):
                url = Cine107S2Query.QUERY_TEMPLATE.format(key=info, pageno=page)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, Cine107S2Query.S2QUERY_EACH_PAGE, {'query': info})

        elif params.step == Cine107S2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的url，获取搜索结果的url，把url写入文件
            info = params.customized['query']
            soup = BeautifulSoup(params.content, 'html.parser')
            titles = soup.select('h3.c-title')
            times = soup.select('span.c-showurl')
            urllist = []
            index = 0
            for result in titles[0:]:
                title = result.get_text().strip()
                nodeUrl = result.select('a')[0].get('href')
                timeStr = times[index].get_text().strip()
               
                if timeStr.find('html') > -1:
                    timeStr = timeStr[timeStr.index('html') + 5:]
                elif timeStr.find('...') > -1:
                    timeStr = timeStr[timeStr.index('...')+4:]
                # 标题中包含指定要查询的关键字，并且是一周内的帖子，对应的url保存
                if self.r.search(ur'(\d+-\d+-\d+)', timeStr):
                    timeStr = self.r.parse(ur'(\d+-\d+-\d+)', timeStr)[0]
                #if title.find(Common.urldec(info)) > -1 and TimeUtility.getuniformtime(timeStr, '%Y-%m-%d') > TimeUtility.getuniformdatebefore(7):
                    #urllist.append(nodeUrl)
                #Logger.getlogging().debug(title)
                #Logger.getlogging().debug(nodeUrl)  
                #Logger.getlogging().debug(Common.urldec(info))
                #Logger.getlogging().debug(title)
                if  compareNow(getuniformtime(timeStr),self.querylastdays):
                    if Common.checktitle(Common.urldec(info), title):
                        urllist.append(nodeUrl) 
                index += 1
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)