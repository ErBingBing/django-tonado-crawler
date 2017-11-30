# -*- coding: utf-8 -*-
################################################################################################################
# @file: funquery.py
# @author: HeDian
# @date:  2016/11/24
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
import json
import math

from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime,compareNow
from configuration import constant
################################################################################################################
# @class：FunS2Query
# @author：HeDian
# @date：2016/11/24
# @note：
################################################################################################################
class FunS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://q1.fun.tv/ajax/filter_videos/?c=0&p={pageno}&word={key}'
    MAIN_DOMAIN = 'http[s]{0,1}://www.fun.tv'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：MofangS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http[s]{0,1}://www.fun.tv/'

    ################################################################################################################
    # @functions：pageprocess
    # @info： 对每页获取数据的处理
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def pageprocess(self, params):
        # Step3: 根据Step2的返回jason数据，获取
        # 标题：jsondata['data'][0开始到19]['title']
        # 连接：jsondata['data'][0开始到19]['url']
        # 视频发布时间：jsondata['data'][0开始到19]['modifydatel'] 这个需要截断前10位，只能对比日期

        info = params.customized['query']
        jsondata = json.loads(params.content)
        searchresult = jsondata['data']

        urllist = []
        for result in searchresult:
            title = result['title']
            url = result['url']
            pubtime = result['modifydate']
            # if not info in title:
            if compareNow(getuniformtime(pubtime), self.querylastdays):
                if Common.checktitle(info, title):
                    urllist.append(self.MAIN_DOMAIN+url)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
            else:
                Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)
        self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
                

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        #keyvalue = Common.urlenc(info)
        keyvalue = Common.urlenc(Common.trydecode(info))
        # step1: 根据key, 拼出下面的url
        # http://q1.fun.tv/ajax/filter_videos/?c=0&p={pageno}&word={key}
        url = FunS2Query.QUERY_TEMPLATE.format(pageno=1, key=keyvalue)
        urls = [url]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == FunS2Query.S2QUERY_FIRST_PAGE:
            #Step2：根据传回的内容，通过xpath: //*[@class="count"] 得到搜索结果总件数。
            # 根据总件数，拼出各个page的url,每个page 20条数据
            # 获取检索结果的Jason返回值
            jsondata = json.loads(params.content)
            count = jsondata['total']
            # 获取不到，则返回
            if int(count) == 0:
                return

            # 检索结果只有1页的场合，直接处理第一页
            if int(count) <= self.DEFAULT_PAGE_SIZE:
                self.pageprocess(params)
            else:
                info = params.customized['query']
                keyvalue = Common.urlenc(Common.trydecode(info))

                page_count = int(math.ceil(float(count) / self.DEFAULT_PAGE_SIZE))
                if page_count > 100:
                    # 该网站只支持最大2000条检索结果
                    page_count = 100
                if page_count >= self.maxpages:
                    page_count = self.maxpages

                # 根据上面的page_count数，拼出所有的搜索结果url
                querylist = []
                for page in range(1, page_count + 1, 1):
                    url = FunS2Query.QUERY_TEMPLATE.format(pageno = page,key = keyvalue)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, FunS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == FunS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的返回jason数据，获取数据
            self.pageprocess(params)