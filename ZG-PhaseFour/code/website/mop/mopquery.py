# -*- coding: utf-8 -*-
##############################################################################################
# @file：MopS2Query.py
# @author：Liyanrui
# @date：2016/11/28
# @version：Ver0.0.0.100
# @note：猫扑论坛页获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from lxml import etree
import math
import datetime
import re
from utility.timeutility import TimeUtility

##############################################################################################
# @class：MopS2Query
# @author：Liyanrui
# @date：2016/11/28
# @note：猫扑论坛页获取元搜的类，继承于SiteS2Query类
##############################################################################################
class MopS2Query(SiteS2Query):
    #MOP_QUERY_TEMPLATE = 'http://search.mop.com/cse/search?q={q}&s=10030666497398670337&p={page}&srt=lds&stp=1&nsid=0&sti={sti}'
    MOP_QUERY_TEMPLATE = 'http://zhannei.baidu.com/cse/search?q={q}&p={page}&sti={sti}&s=10030666497398670337'
    PAGE_SIZE = 10
    MOP_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    MOP_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/28
    # @note：猫扑论坛页元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://mop.com/'

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        info_enc = Common.urlenc(info)
        sti = self.querylastdays*24*60
        urls = [MopS2Query.MOP_QUERY_TEMPLATE.format(q=info_enc, page =0,sti = sti)]
        self.__storeqeuryurllist__(urls, self.MOP_S2QUERY_FIRST_PAGE, {'query': info,'sti':sti})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
        if params.step == MopS2Query.MOP_S2QUERY_FIRST_PAGE:
            # 获得首页url参数
            info = params.customized['query']
            info_enc = Common.urlenc(info)
            sti = params.customized['sti']
            # 取得总件数
            content = etree.HTML(params.content)
            comments_count = content.xpath('//*[@id="results"]/span')
            if len(comments_count) == 0:
                return
            comments_count = comments_count[0].text
            comments_count = comments_count.replace(',','')
            # comments_count = int(re.findall(ur'为您找到相关结果(\d+)个', comments_count)[0])
            comments_count = int(re.findall(ur'(\d+)', comments_count)[0])

            # 所有循环列表
            querylist = []
            pagenum = int(math.ceil(float(comments_count) / MopS2Query.PAGE_SIZE))
            if pagenum >= self.maxpages:
                pagenum = self.maxpages

            # 根据总页数，获取query列表
            for page in range(0, pagenum, 1):
                url = MopS2Query.MOP_QUERY_TEMPLATE.format(
                    q=info_enc,
                    page=page,sti=sti)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, MopS2Query.MOP_S2QUERY_EACH_PAGE, {'query': info})

        # 从查询页面中获取视频URL
        elif params.step == MopS2Query.MOP_S2QUERY_EACH_PAGE:
            # 获取文本
            content = etree.HTML(params.content)
            # 获取该页超级链接
            hrefs = content.xpath('//*[@class="c-title"]/a/@href')
            urllist = []
            otherurlpatterns = ['https?://(3g|m|xuzhou|l)\.mop\.com.*',
                                'https?://(www|tag)\.mop\.com.*',
                                '^https?://.*\.mop\.com/$',
                                'https?://hi\.mop\.com/space/',
                                'list.html',
                                'http://auto\.mop\.com/\w{2,}/.*']
            for href in hrefs:
                for other in otherurlpatterns:
                    if re.search('http://auto\.mop\.com/n\d+.s?html', href):
                        urllist.append(href)
                        continue
                    if re.search(other,href):
                        #print href + '------' + other
                        break
                else:
                    if href not in urllist:
                        urllist.append(href)
            # 获取最终url列表
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)