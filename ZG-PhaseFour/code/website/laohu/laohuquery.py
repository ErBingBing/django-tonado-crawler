# -*- coding: utf-8 -*-
##############################################################################################
# @file：laohuS2Query.py
# @author：HuBorui
# @date：2016/11/28
# @version：Ver0.0.0.100
# @note：老虎游戏论坛获取元搜的文件
###############################################################################################
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA, SPIDER_S2_WEBSITE_TYPE, SPIDER_CHANNEL_S1
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from utility.common import Common
from website.common.s2query import SiteS2Query
import re
import datetime
from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility

##############################################################################################
# @class：laohuS2Query
# @author：HuBorui
# @date：2016/11/28
# @note：老虎游戏论坛获取元搜的类，继承于SiteS2Query类
##############################################################################################
class LaohuS2Query(SiteS2Query):
    #LAOHU_QUERY_TEMPLATE = 'http://bbs.laohu.com/plugin.php?id=esearch&mymod=search&myac=thread&word={KEY}&page={pn}'
    LAOHU_QUERY_TEMPLATE = 'http://bbs.laohu.com/plugin.php?id=esearch&mymod=search&myac=thread&word={KEY}&page={pn}&srchfrom={time}'
    LAOHU_S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    LAOHU_S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    LAOHU_MAIN_DOMAIN = 'http://bbs.laohu.com/'
    LAOHU_LINK = 'http://bbs.laohu.com/thread-{tid}-1-1.html'
    DEFAULT_TIME = 86400
    tids = []
    

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/28
    # @note：老虎游戏论坛元搜类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://bbs.laohu.com/'
        self.r = RegexUtility()
        self.inputtime = self.querylastdays

    def preprocess(self,mid_url):        
        if self.r.search('tid=\d+',mid_url):
            tid = self.r.parse('tid=(\d+)',mid_url)[0] 
            if len(self.tids) == 0:
                self.tids.append(tid)
                newurl = self.LAOHU_LINK.format(tid=tid)                
            else:
                if tid not in self.tids:
                    self.tids.append(tid)
                    newurl = self.LAOHU_LINK.format(tid=tid)
                else:
                    newurl = None
        else:
            newurl = self.LAOHU_MAIN_DOMAIN + mid_url
        return newurl
    
        
    ################################################################################################################
    # @functions：pageprocess
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################   
    def pageprocess(self, params):
        # 获取文本
        xparser = XPathUtility(params.content)
        # 获取该页超级链接
        hreflist = xparser.xpath('//h3/a/@href')
        hrefs = []
        for mid_url in hreflist:
            mid = self.preprocess(mid_url)
            if mid is not None:                
                hrefs.append(mid) 
    
        # 获取该页内容的所有发布时间
        publictime = xparser.xpath('//*[@class="scontent"]/text()[1]')
        publicTimes = []
        for timeindex in publictime:
            middle = str(timeindex).replace('\n','').replace('\t','').strip()
            publicTimes.append(str(str(middle).split(' ')[0]) + ' ' + str(str(middle).split(' ')[1]))
        # 获取改页所有title
        titles = []
        titles_list = xparser.getlist('//h3')
        for title in titles_list:
            mid_title = str(title).replace('\n','').replace('\t','').strip()
            titles.append(mid_title)
        # 获取关键字
        KEY_mid = params.customized['KEY']
        KEY = Common.urldec(KEY_mid)
        # 获取标题正则表达式
        titlePatten = KEY
        # 获取一周前日期
        today = datetime.datetime.now()
        before_days = today + datetime.timedelta(-self.inputtime)
        before_arr = str(before_days).split('.')
        before_time = before_arr[0]
    
        urllist = []
        len_hrefs = len(hrefs)
        number = 0
        for index in publicTimes[:len_hrefs]:
            # 是否是标题命中
            # mid_value = re.compile(titlePatten)
            # flg = mid_value.search(str(titles[number]))
            flg = Common.checktitle(titlePatten, str(titles[number]))
            # 是当前一周内发布视频，并且标题命中的场合
            if index > before_time and flg:
                url = hrefs[number]
                urllist.append(url)
            number = number + 1
    
        # 获取最终url列表
        if len(urllist) > 0:
            self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
    
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        urlkey = Common.urlenc(info)
        time = self.querylastdays*LaohuS2Query.DEFAULT_TIME
        urls = [LaohuS2Query.LAOHU_QUERY_TEMPLATE.format( KEY = urlkey, pn = 1 ,time = time)]
        self.__storeqeuryurllist__(urls, self.LAOHU_S2QUERY_FIRST_PAGE, {'KEY': urlkey,'time' : time})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        # 从搜索首页面中获取的搜索结果数量，生成搜索页面URL
        if params.step == LaohuS2Query.LAOHU_S2QUERY_FIRST_PAGE:
            # 获得首页url参数
            KEY = params.customized['KEY']
            time = params.customized['time']
            #获取总页数
            xparser = XPathUtility(params.content)
            pageCounts = xparser.getlist('//*[@id="main"]/div[2]/span')
            if len(pageCounts) > 0:
                page = str(pageCounts[0]).split('/')[1]                
                
                #获取第一页的搜索结果
                self.pageprocess(params)

                if int(page) > 1:
                    if int(page) >= self.maxpages:
                        page = self.maxpages
                    querylist = []
                    # 根据总页数，获取query列表(第一页的数据已经获取到了，从第二页开始拼出获取的url)
                    for pages in range(2, int(page) + 1, 1):
                        url = LaohuS2Query.LAOHU_QUERY_TEMPLATE.format(KEY = KEY,pn = pages,time = time)
                        querylist.append(url)
                    self.__storeqeuryurllist__(querylist, LaohuS2Query.LAOHU_S2QUERY_EACH_PAGE, {'KEY': KEY})
                    
            else:
                Logger.getlogging().debug('抱歉，没有找到与' + ' '+ KEY +' '+'相关的帖子')

        # 从查询页面中获取视频URL
        elif params.step == LaohuS2Query.LAOHU_S2QUERY_EACH_PAGE:
            self.pageprocess(params)
