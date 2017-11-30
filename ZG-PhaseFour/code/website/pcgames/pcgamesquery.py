# -*- coding: utf-8 -*-
################################################################################################################
# @file: .py
# @author: Merlin.W.ouyang
# @date:  2016/11/29
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from lxml import etree

from configuration.environment.configure import SpiderConfigure
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
import datetime
from utility.timeutility import TimeUtility
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA

################################################################################################################
# @class：dm78dmQuery
# @author：Merlin.W.ouyang
# @date：2016/11/26
# @note：
################################################################################################################
########################################################################
class  S2Query(SiteS2Query):
    S2_URL='http://ks.pcgames.com.cn/games_bbs.jsp?q=%s&scope=all&scope=title&sort=score,date&pageNo=%s'
    STEP_1 = 1
    STEP_2 = 2
    
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：AcFunQuery，初始化内部变量
    ################################################################################################################
    #----------------------------------------------------------------------
    def __init__(self):
        SiteS2Query.__init__(self)
        self.r = RegexUtility()
        self.pagelimit = self.maxpages
        self.fakeoriginalurl='http://bbs.pcgames.com.cn/topic-7979.html'
        self.querylastdays = SpiderConfigure.getinstance().getlastdays()

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################        
    #----------------------------------------------------------------------
    def query(self,info):
        Logger.getlogging().info("query")
        #querykey=Common.urlenc(info)
        querykey=self.querykey2urlenc(info)
        query_url = [S2Query.S2_URL % (querykey, '1')]
        Logger.getlogging().debug(query_url[0])
        self.__storeqeuryurllist__(query_url, self.STEP_1, 
                                   {'key':querykey,
                                    'pageno':'1'})
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    #----------------------------------------------------------------------  
    
    def  process(self,params):
        if params.step == S2Query.STEP_1:
            html = etree.HTML(params.content)
            isblack = False
            #判断页面是不是空的
            try:
                contenttext=html.xpath('//div[@class="attentionTitle"]/text()')
                if contenttext<>[]:
                    isblack = True
            except:
                isblack=False
            #不是空的情况下，判断是不是又翻页
            if isblack == False:
                try:
                    page = html.xpath('//*[@class="pcgames_page"]/a/text()')[-2]
                except:
                    page = '1'
                index =0
                urllist=[]
                if self.pagelimit:
                    if int(page) > self.pagelimit:
                        Logger.getlogging().warning('the pageMaxNumber is shutdown to {0}'.format(self.pagelimit))
                        page = self.pagelimit
                for index in range(0,int(page)):
                    searchurl = S2Query.S2_URL % (params.customized['key'],str(index+1))
                    urllist.append(searchurl)
                self.__storeqeuryurllist__(urllist, S2Query.STEP_2,{'key':params.customized['key'],'page':page})
        elif params.step == S2Query.STEP_2:
            html = etree.HTML(params.content)
            #正式环境获得数据库记载的上一次获取时候的最新评论的时间
            #urlcommentinfo= URLStorage.geturlcommentinfo().updatetime
            #测试环境模拟数据
            urlcommentinfo = (datetime.datetime.now() + datetime.timedelta(days=-int(self.querylastdays))).strftime('%Y-%m-%d %H:%M:%S')            
            urllist = html.xpath('//div[@class="resultList"]/ul/li/p/a[1]/@href')
            pbtime=html.xpath('//*[@class="resultList"]/ul/li/span[1]/text()')
            index =0
            url=[]
            for index in range(0,len(pbtime)):
                pbtime[index]=pbtime[index].replace('-','').strip()
                pbtime[index]=TimeUtility.getuniformtime(pbtime[index], '%a %b %d %H:%M:%S CST %Y')
                if pbtime[index]>urlcommentinfo:
                    url.append(urllist[index])
            if len(url)>0:
                self.__storeurllist__(url,SPIDER_S2_WEBSITE_TIEBA)
            
            