# -*- coding: utf-8 -*-
################################################################################################################
# @file: iqiyiquery.py
# @author: HeDian
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_TYPE
from lxml import etree
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from bs4 import BeautifulSoup 
from utility.timeutility import TimeUtility
from configuration import constant

################################################################################################################
# @class：iqiyiquery
# @author：HeDian
# @date：2016/11/22
# @note：
################################################################################################################
class IqiyiS2Query(SiteS2Query):
    IQIYI_QUERY_TEMPLATE = 'http://so.iqiyi.com/so/q_{key}_ctg__t_0_page_{pageno}_p_1_qc_0_rd_2_site_iqiyi_m_4_bitrate_?af=true'
    DEFAULT_PAGE_SIZE = 20
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：IqiyiS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://www.iqiyi.com/'

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
        # step1: 根据key, 拼出下面的url(最新1周）
        urls = [IqiyiS2Query.IQIYI_QUERY_TEMPLATE.format(key = keyvalue, pageno = 1)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == IqiyiS2Query.S2QUERY_FIRST_PAGE:
            #Step2: 根据返回内容，通过xpath: //*[@data-search-page="item"] 得到最大page数、（返回数组的倒数第二位）
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            html = etree.HTML(params.content)
            nodes = html.xpath('//*[@data-search-page="item"]/text()')
            # 获取最后一页的页数（数组最后一项是下一页，倒数第二项是最后一页的页码数）
            if len(nodes) != 0:
                page_count = int(nodes[-2])
            else:
                page_count = 1
        
            # 根据上面的page_count数，拼出所有的搜索结果url(最新1周）
            # http://so.iqiyi.com/so/q_Key_ctg__t_0_page_Page数_p_1_qc_0_rd_2_site_iqiyi_m_4_bitrate_?af=true
            querylist = []
            if page_count >= self.maxpages:
                page_count = self.maxpages
            for page in range(1, page_count + 1, 1):
                url = IqiyiS2Query.IQIYI_QUERY_TEMPLATE.format(key = keyvalue, pageno = page)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, IqiyiS2Query.S2QUERY_EACH_PAGE, {'query':info})

        elif params.step == IqiyiS2Query.S2QUERY_EACH_PAGE:
            # Step3: 根据Step2的url，通过xpath://*[@class="result_title"]/a/@href 获取搜索结果的url，把url写入文件
            query = params.customized['query']
            soup = BeautifulSoup(params.content, 'html5lib')
            divs = soup.select('.mod_result_list > .list_item')
            urllist = []
            for div in divs:
                try:
                    url = div.select_one('.result_title > a').get('href')
                    curtime = div.select_one('.result_info_desc')
                    # curtime = div.select_one('.result_info_desc').get_text()
                    if not curtime:
                        continue
                    else:
                        curtime = curtime.get_text()
                    title = div.select_one('.result_title > a').get_text().strip()
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
            if len(urllist) > 0:
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
