# -*- coding: utf-8 -*-
##############################################################################################
# @file：Lequery.py
# @author：Liyanrui
# @date：2016/11/25
# @version：Ver0.0.0.100
# @note：乐视获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
import math
import json
import re
import datetime
from utility.regexutil import RegexUtility
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from configuration import constant
##############################################################################################
# @class：LetvQuery
# @author：Liyanrui
# @date：2016/11/25
# @note：乐视获取元搜的类，继承于SiteS2Query类
##############################################################################################
class LeQuery(SiteS2Query):
    LETV_QUERY_TEMPLATE = 'http://search.lekan.le.com/lekan/apisearch_json.so?from=pc&or=1&pn={pn}&ps=30&wd={q}'
    DEFAULT_PAGE_SIZE = 30
    LETV_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    LETV_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/25
    # @note：乐视搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.le.com/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls = [LeQuery.LETV_QUERY_TEMPLATE.format(pn=1, q=q)]
        self.__storeqeuryurllist__(urls, self.LETV_S2QUERY_FIRST_PAGE, {'query': q})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
        if params.step == LeQuery.LETV_S2QUERY_FIRST_PAGE:
            # 获得首页url参数
            q = params.customized['query']
            content = json.loads(params.content)
            count = content['video_count']
            if int(count) == 0:
                Logger.getlogging().info('count:{count}'.format(count=count))
                return

            # 所有循环列表
            querylist = []
            if count > 510:
                totalpage = 17
            else:
                totalpage = int(math.ceil(float(count) / LeQuery.DEFAULT_PAGE_SIZE))
             
            # 获取第一页的搜索结果
            self.gets2url(params)
            if totalpage > self.maxpages:
                totalpage = self.maxpages
            # 根据总页数，获取query列表(第一页已经获取到了，从第二页开始获取）
            for page in range(2, totalpage + 1, 1):
                url = LeQuery.LETV_QUERY_TEMPLATE.format(
                    pn=page,
                    q=params.customized['query'])
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, LeQuery.LETV_S2QUERY_EACH_PAGE, {'query': q})

        # 从查询页面中获取视频URL
        elif params.step == LeQuery.LETV_S2QUERY_EACH_PAGE:
            self.gets2url(params)

    ################################################################################################################
    # @functions：gets2url
    # @params： see WebSite.process
    # @return：none
    # @note：从查询数据中得到url
    ################################################################################################################
    def gets2url(self, params):
        # 获取文本
        contents = json.loads(params.content)  
        query = Common.urldec(params.customized['query'])
        urllist = []
        for item in contents['video_list']:
            try:
                vid = item['vid']
                if item.get('categoryName', '') == u"体育":
                    url = 'http://sports.le.com/video/{vid}.html'.format(vid=vid)
                else:
                    url = 'http://www.le.com/ptv/vplay/{vid}.html'.format(vid=vid)
                curtime = item['ctime']
                #print TimeUtility.getuniformtime(curtime)
                title = item['name']
                if self.compareNow(curtime):
                    if self.checktitle(query, title):
                        #Logger.getlogging().info(title)
                        urllist.append(url)
                    else:
                        Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                else:
                    Logger.log(url, constant.ERRORCODE_WARNNING_NOMATCHTIME)   
            except:
                Logger.printexception()        
        # 获取最终url列表
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)