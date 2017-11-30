# -*- coding: utf-8 -*-
################################################################################################################
# @file: sinaquery.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:49
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/1/12 16:50
# @note:修改了标题命中,添加了85-59行代码
################################################################################################################
import json
import math

from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, CHARSET_UTF8
from utility.common import Common
from website.common.s2query import SiteS2Query
from bs4 import BeautifulSoup
import re
from log.spiderlog import Logger


################################################################################################################
# @class：sinaquery
# @author：Sun Xinghua
# @date：2016/11/21 9:49
# @note：
################################################################################################################
class SinaS2Query(SiteS2Query):
    SINA_QUERY_TEMPLATE = 'http://so.video.sina.com.cn/interface/s?from=video&wd={q}&s_id=w00001&p={ps}&n={pn}&s=1&pf={pf}'
    DEFAULT_PAGE_SIZE = 50
    SINA_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    SINA_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SinaS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://video.sina.com.cn/'

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q=Common.urlenc(Common.urlenc(info))
        urls = [SinaS2Query.SINA_QUERY_TEMPLATE.format(q=q, ps=1, pn=1, pf=self.querylastdays)]
        self.__storeqeuryurllist__(urls, self.SINA_S2QUERY_FIRST_PAGE, {'query': info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
        if params.step == SinaS2Query.SINA_S2QUERY_FIRST_PAGE:
            jsdata = json.loads(params.content)
            count = int(jsdata['total'])
            querylist = []
            if count > 0:
                for page in range(1, int(math.ceil(float(count) / SinaS2Query.DEFAULT_PAGE_SIZE)) + 1, 1):
                    url = SinaS2Query.SINA_QUERY_TEMPLATE.format(
                        q=Common.urlenc(params.customized['query']),
                        ps=page,
                        pn=SinaS2Query.DEFAULT_PAGE_SIZE,
                        pf=self.querylastdays)
                    querylist.append(url)
                self.__storeqeuryurllist__(querylist, SinaS2Query.SINA_S2QUERY_EACH_PAGE, {'query': params.customized['query']})
        # 从查询页面中获取视频URL
        elif params.step == SinaS2Query.SINA_S2QUERY_EACH_PAGE:
            jsdata = json.loads(params.content)
            searchlist = jsdata['list']
            urllist = []
            try:
                for search in searchlist:
                    # if params.customized['query'].decode(CHARSET_UTF8) in search['videoname']:
                    title = search['videoname']
                    if re.search('<.*>[\s\S]*?</.*>',title):
                        soup = BeautifulSoup(title,'html5lib')
                        title = soup.get_text()
                        title = ''.join(title.strip().split())
                        Logger.getlogging().debug(title)
                    #if Common.checktitle(params.customized['query'], search['videoname']):
                    if Common.checktitle(params.customized['query'], title):
                        urllist.append(search['url'])

                if len(urllist) > 0:
                    self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
            except:
                Logger.printexception()
