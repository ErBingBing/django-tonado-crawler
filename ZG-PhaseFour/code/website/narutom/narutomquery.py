# -*- coding: utf-8 -*-
################################################################################################################
# @file: narutomquery.py
# @author: HeDian
# @date:  2016/11/23
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
import math
from lxml import etree
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.gettimeutil import getuniformtime,compareNow


################################################################################################################
# @class：NarutomS2Query
# @author：HeDian
# @date：2016/11/23
# @note：
################################################################################################################
class NarutomS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'http://search.narutom.com/cse/search?q={key}&p={pageno}&s=7660238846226745217&entry=1'
    FIRST_PAGE = 'http://search.narutom.com/cse/search?s=7660238846226745217&entry=1&q={key}'
    DEFAULT_PAGE_SIZE = 10
    MAX_COUNT = 750
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：NarutomS2Query类构造器，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.narutom.com/'
        self.r = RegexUtility()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        Logger.getlogging().info("query")
        keyvalue = Common.urlenc(info)

        #Step1：根据key, 拼出下面的url（不能设置最新和一周检索条件）
        #http://search.narutom.com/cse/search?s=7660238846226745217&entry=1&ie=gbk&q=key的urlcode
        url = NarutomS2Query.FIRST_PAGE.format(key=keyvalue)
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
        if params.step == NarutomS2Query.S2QUERY_FIRST_PAGE:
            #Step2： 根据返回的url,通过xpath://*[@id="results"]/span 得到搜索结果总件数，根据总件数，拼出搜索结果的url，写文件保存
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[@id="results"]/span')
            # 获取不到，则返回
            if len(nodes) == 0:
                return

            # 获取总检索件数（例如：为您找到相关结果1,307个）
            count = 0
            totalstr = nodes[0].text.replace(',','')
            if self.r.search(u'\d+', totalstr):
                countstr = self.r.parse(u'(\d+)',totalstr)[0]
                count = int(countstr)
                # 该网站最多能获得750件检索结果
                if count > self.MAX_COUNT:
                    count = self.MAX_COUNT
            else:
                return


            # 根据上面的count数，拼出所有的搜索结果url
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            page_count = float(count / self.DEFAULT_PAGE_SIZE)
            firstpage = NarutomS2Query.FIRST_PAGE.format(key=keyvalue)
            querylist = []
            querylist.append(firstpage)
            if count > 10:
                #第二页的page数是1，第三页是2...... page数范围是：1-74(表示第2页-第75页）
                for page in range(1, int(math.ceil(page_count)), 1):
                    url = NarutomS2Query.QUERY_TEMPLATE.format(key = keyvalue, pageno = page)
                    querylist.append(url)

            self.__storeqeuryurllist__(querylist, NarutomS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == NarutomS2Query.S2QUERY_EACH_PAGE:
            # Step3：根据Step2的返回结果，通过xpath: //*[@id="results"]/div/h3/a/@href 获得搜索结果的url,把url写入文件
            info = params.customized['query']
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[@id="results"]/div/h3/a/@href')
            #titles = html.xpath('//*[@id="results"]/div/h3/a')
            pubtimestr = html.xpath('//*[@class="c-showurl"]')

            datecheck = False
            if len(pubtimestr) == len(nodes):
                datecheck = True

            urllist = []
            for index in range(0, len(nodes), 1):
                # if titles[index] is not None and titles[index].find(info) > -1:
                # if titles[index] is not None and Common.checktitle(info, titles[index]):
                    # 标题中包含指定要查询的关键字，对应的url保存
                if datecheck:
                    # 如果xpath获取到了包含时间的字符串，检查时间
                    if self.r.search('(\d+-\d+-\d+)', pubtimestr[index].text):
                        pubtime = getuniformtime(self.r.parse('(\d+-\d+-\d+)', pubtimestr[index].text)[0])
                        if compareNow(pubtime, int(self.querylastdays)):
                            urllist.append(nodes[index])
                else:
                    urllist.append(nodes[index])

            '''
            urllist = []
            for node in nodes:
                urllist.append(node)
            '''
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)