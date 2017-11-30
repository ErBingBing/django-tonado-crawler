# -*- coding: utf-8 -*-
##############################################################################################
# @file：kumiS2Query.py
# @author：Liyanrui
# @date：2016/11/24
# @version：Ver0.0.0.100
# @note：酷米网动漫网获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from utility.common import Common
from website.common.s2query import SiteS2Query
from lxml import etree
import datetime
from utility.regexutil import RegexUtility
from configuration.environment.configure import SpiderConfigure
from bs4 import BeautifulSoup
import re

##############################################################################################
# @class：kumiS2Query
# @author：Liyanrui
# @date：2016/11/24
# @note：酷米网动漫网获取元搜的类，继承于SiteS2Query类
##############################################################################################
class kumiS2Query(SiteS2Query):
    KUMI_QUERY_TEMPLATE = 'http://so.kumi.cn/list.php?q={q}&button=+/'
    KUMI_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/24
    # @note：酷米网动漫网搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.kumi.cn/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls = [kumiS2Query.KUMI_QUERY_TEMPLATE.format(q=q)]
        self.__storeqeuryurllist__(urls, self.KUMI_S2QUERY_FIRST_PAGE, {'query': info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
        if params.step == kumiS2Query.KUMI_S2QUERY_FIRST_PAGE:
            # 获得首页url参数
            titlePatten = params.customized['query']
            # 获取标题正则表达式
            soup = BeautifulSoup(params.content,'html5lib')
            boxs = soup.find_all(attrs={'class':re.compile('seaResultBox')})
            if boxs:
                urllist = []
                for box in boxs:
                    title = box.select_one('.seaResultA > a').get_text()
                    if not Common.checktitle(titlePatten, title):
                        continue
                    url = box.select_one('.seaResultA > a').get('href')
                    urllist.append(url)
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
                    

     