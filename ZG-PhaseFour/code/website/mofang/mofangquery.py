# -*- coding: utf-8 -*-
################################################################################################################
# @file: mofangquery.py
# @author: HeDian
# @date:  2016/11/24
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/02/10
# @note:添加了使用json.loads时的异常处理，异常码：40000
################################################################################################################
import json
import math
import datetime
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from utility.timeutility import TimeUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.gettimeutil import getuniformtime,compareNow


################################################################################################################
# @class：MofangS2Query
# @author：HeDian
# @date：2016/11/24
# @note：
################################################################################################################
class MofangS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://www.mofang.com/index.php?m=search&a=json_init&q={key}&type=video&page={pageno}&pagesize={pagesize}'
    QUERY_TEMPLATE_BBS = 'http://bbs.mofang.com/searchThread?keyword={key}&p={pageno}&pagesize={pagesize}'
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
        self.r = RegexUtility()
        self.fakeoriginalurl = 'http://www.mofang.com/'

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
        # step1: 根据key, 拼出下面的url
        # http://www.mofang.com/index.php?m=search&a=json_init&q={key}&type=video&page={页数}&pagesize=1
        # 视频S2
        urls = [MofangS2Query.QUERY_TEMPLATE.format(key = keyvalue, pageno = 1, pagesize = 1)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

        # 2016/12/20 测试时发现，该论坛的搜索功能改为discuz 为Post获取数据，因此关闭论坛S2功能。
        # 论坛S2
        # urls = [MofangS2Query.QUERY_TEMPLATE_BBS.format(key=keyvalue, pageno=1, pagesize=20)]
        # Logger.getlogging().debug(urls[0])
        # self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if self.r.match(r'^http://www\.mofang\.com/.*', params.url):
            self.processVideo(params)
        # else:
        #     self.processBBS(params)

    ################################################################################################################
    # @functions：processVideo
    # @params： see WebSite.processVideo
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def processVideo(self, params):
        if params.step == MofangS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回json内容，comments['totalnums'] 得到视频总数
            #一个json返回20条数据，需要使用总数除以20获得总页数，然后在写到page参数里面
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            try:
                jsondate = json.loads(params.content)
                comments_count = jsondate['totalnums']
            except:
                Logger.getlogging().warning('{}:40000'.format(params.url))
                return 
            # 获取不到，则返回
            if int(comments_count) == 0:
                return

            page_count = int(math.ceil(float(comments_count) / self.DEFAULT_PAGE_SIZE))
            # 根据上面的page_count数，拼出所有的搜索结果url(最新1周）
            querylist = []
            if page_count > 0:
                for page in range(1, page_count + 1, 1):
                    url = MofangS2Query.QUERY_TEMPLATE.format(key = keyvalue, pageno = page, pagesize = self.DEFAULT_PAGE_SIZE)
                    Logger.getlogging().debug(url)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, MofangS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == MofangS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的返回jason数据，获取
            # 标题：comments['data'][0开始到19]['title']
            # 连接：comments['data'][0开始到19]['url']
            # 视频发布时间：comments['data'][0开始到19]['inputtime'] 这个需要截断前10位，只能对比日期

            info = params.customized['query']
            try:
                jsondate = json.loads(params.content)
                searchresult = jsondate['data']
            except:
                Logger.getlogging().warning('{}:40000'.format(params.url))
                return             

            # 获取当前日(日期类型)
            today = datetime.datetime.strptime(TimeUtility.getcurrentdate(), TimeUtility.DATE_FORMAT_DEFAULT)

            urllist = []
            for index in range(0, len(searchresult), 1):
                #print searchresult[index]['title']
                #print searchresult[index]['inputtime']
                if searchresult[index]['title'] is not None:
                    # 标题中包含指定要查询的关键字，对应的url保存
                    # if searchresult[index]['title'].find(info) > -1:
                    if Common.checktitle(info, searchresult[index]['title']):
                        if searchresult[index]['inputtime'] is not None:
                            #inputtime = datetime.datetime.strptime(TimeUtility.getuniformtime2(int(searchresult[index]['inputtime'])), TimeUtility.TIME_FORMAT_DEFAULT)
                            #intervaldays = today - inputtime
                            #if intervaldays.days <= int(self.querylastdays):
                            pubtime = getuniformtime(str(searchresult[index]['inputtime']))
                            
                            if compareNow(pubtime,int(self.querylastdays)):
                                urllist.append(searchresult[index]['url'])
                        else:
                            # 获取不到发布时间，则默认为周期以内
                            urllist.append(searchresult[index]['url'])

            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)

    ################################################################################################################
    # @functions：processBBS
    # @params： see WebSite.processBBS
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def processBBS(self, params):
        if params.step == MofangS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回json内容，comments['totalnums'] 得到视频总数
            #一个json返回20条数据，需要使用总数除以20获得总页数，然后在写到page参数里面
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            try:
                jsondate = json.loads(params.content)
                comments_count = jsondate['data']['total']
            except:
                Logger.getlogging().warning('{}:40000'.format(params.url))
                return             
            # 获取不到，则返回
            if int(comments_count) == 0:
                return

            page_count = int(math.ceil(float(comments_count) / self.DEFAULT_PAGE_SIZE))
            # 根据上面的page_count数，拼出所有的搜索结果url(最新1周）
            querylist = []
            if page_count > 0:
                for page in range(1, page_count + 1, 1):
                    url = MofangS2Query.QUERY_TEMPLATE_BBS.format(key=keyvalue, pageno=page, pagesize=self.DEFAULT_PAGE_SIZE)
                    Logger.getlogging().debug(url)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, MofangS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == MofangS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的返回jason数据，获取
            # 标题：comments['data']['threads'][0开始到19]['subject']
            # 连接：comments['data']['threads'][0开始到19]['link_url']
            # 视频发布时间：comments['data']['threads'][0开始到19]['create_time'] 这个需要截断前10位，只能对比日期

            info = params.customized['query']
            try:
                jsondate = json.loads(params.content)
                searchresult = jsondate['data']['threads']
            except:
                Logger.getlogging().warning('{}:40000'.format(params.url))
                return         

            # 获取当前日(日期类型)
            today = datetime.datetime.strptime(TimeUtility.getcurrentdate(), TimeUtility.DATE_FORMAT_DEFAULT)

            urllist = []
            for index in range(0, len(searchresult), 1):

                if searchresult[index]['subject'] is not None:
                    # 标题中包含指定要查询的关键字，对应的url保存
                    # if searchresult[index]['subject'].find(info) > -1:
                    if Common.checktitle(info, searchresult[index]['subject']):
                        if searchresult[index]['create_time'] is not None:
                            #inputtime = datetime.datetime.strptime(TimeUtility.getuniformtime2(int(searchresult[index]['create_time'])), TimeUtility.TIME_FORMAT_DEFAULT)
                            #intervaldays = today - inputtime
                            #if intervaldays.days <= int(self.querylastdays):
                                #urllist.append(searchresult[index]['link_url'])
                            inputtime = getuniformtime(str(searchresult[index]['create_time']))
                            
                            if compareNow(inputtime,int(self.querylastdays)):
                                urllist.append(searchresult[index]['link_url'])                            
                        else:
                            # 获取不到发布时间，则默认为周期以内
                            urllist.append(searchresult[index]['link_url'])

            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)