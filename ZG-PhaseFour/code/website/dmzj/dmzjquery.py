# -*- coding: utf-8 -*-
################################################################################################################
# @file: dmzjquery.py
# @author: HeDian
# @date:  2016/11/23
# @version: Ver0.0.0.100
# @note:
# @modify
# @author:Jiangsiwei
# @date:2017/01/16
# @note:第69行，取标题时取的为tag对象，应该取属性值；第70行，已修改添加属性方法get_text()
################################################################################################################
import json
from lxml import etree
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from bs4 import BeautifulSoup
import re
from website.common.bbss2postquery import BBSS2PostQuery 

########################################################################
class DmzjQuery(SiteS2Query):
    """"""
    #包含get和post请求的不同query
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        SiteS2Query.__init__(self)
        self.post_url = 'http://bbs.dmzj.com/search.php?mod=forum'
        self.get_url = 'http://donghua.dmzj.com'
        pass
    
    #----------------------------------------------------------------------
    def  creatobject(self):
        """创建具体的类对象
           !!!注意DmzjS2Query,BBSS2PostQuery类的初始化要有parent参数"""
        self.getQuery = DmzjS2Query(self)
        self.postQuery = BBSS2PostQuery(self.post_url,parent=self)
        
    #----------------------------------------------------------------------
    def  query(self,info):
        """分别调用多个query"""
        self.creatobject()
        self.getQuery.query(info)
        self.postQuery.query(info)
        
    #----------------------------------------------------------------------
    def process(self,params):
        """调用具体的取url列表步骤"""
        try:
            if params.step == DmzjS2Query.S2QUERY_FIRST_PAGE:
                self.getQuery.step2(params)
            if params.step == DmzjS2Query.S2QUERY_EACH_PAGE:
                self.getQuery.pageprocess(params)
            if params.step == BBSS2PostQuery.S2QUERY_FIRST_PAGE:
                self.postQuery.step1(params)
            if params.step == BBSS2PostQuery.S2QUERY_EACH_PAGE:
                self.postQuery.step2(params)    
        except:
            Logger.printexception()

        
################################################################################################################
# @class：DmzjS2Query
# @author：HeDian
# @date：2016/11/23
# @note：
################################################################################################################
class DmzjS2Query(SiteS2Query):
    QUERY_TEMPLATE = 'https://s.acg.dmzj.com/dh/index.php?c=search&m=dosearch&s={key}&p={pageno}&callback=dealResult'
    FIRST_PAGE = 'https://donghua.dmzj.com/search.html?s={key}'
    MAIN_DOMAIN = 'https://donghua.dmzj.com'
    DEFAULT_PAGE_SIZE = 10
    S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：IqiyiS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self,parent = None):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://donghua.dmzj.com/'
        self.r = RegexUtility()
        if parent:
            self.website = parent.website

    ################################################################################################################
    # @functions：pageprocess
    # @info： 对每一页获取的检索结果进行处理
    # @return：none
    # @note：需要标题命中,因为无法获取时间信息，所以不能按指定周期获得结果
    ################################################################################################################
    def pageprocess(self, params):
        # Step3：根据返回的html，通过xpath://*[@class="scout_anim_titletext"],获得检索结果的标题
        # //*[@class="scout_anim_title"]/div/a/@href，获得检索结果的url
        #Logger.getlogging().debug(params.content)
        indexstart = params.content.find('(')
        indexstop = params.content.rfind(')')
        if indexstart > -1 and indexstop > -1:
            jsonvalue = params.content[indexstart + 1:indexstop]
            jsondata = json.loads(jsonvalue)
            info = params.customized['query']
            soup = BeautifulSoup(jsondata['content'],'html5lib')
            uls = soup.select('.scout_anim_odd > .scout_anim_odd_ul')
            if uls:
                for ul in uls:
                    #titles = ul.select_one('.scout_anim_titletext')
                    titles = ul.select_one('.scout_anim_titletext').get_text()
                    Logger.getlogging().debug(titles)
                    # if info not in titles:
                    if not Common.checktitle(info, titles):
                        return 
                    content = ul.select('.scout_anim_content > div > ul > li')
                    if content:
                        if len(content) > 3:
                            content = content[-3:]
                        urllist = ['https://donghua.dmzj.com'+item.find('a').get('href') for item in content]
                        self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
                        
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
        # http://donghua.dmzj.com/search.html?s=Key的urlcode
        urls = [DmzjS2Query.QUERY_TEMPLATE.format(key=keyvalue, pageno=1)]
        Logger.getlogging().debug(urls[0])
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'query':info})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        if params.step == DmzjS2Query.S2QUERY_FIRST_PAGE:
            self.step2(params)

        elif params.step == DmzjS2Query.S2QUERY_EACH_PAGE:
            self.pageprocess(params)
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        #Step2：根据返回的html，通过xpath://*[@id="bottom_pagebar"]/div/span, 获取到总页数（例如：总共2页）
        #根据总页数，拼出各个页面的url，并保存
        indexstart = params.content.find('(')
        indexstop = params.content.rfind(')')
        if indexstart > -1 and indexstop > -1:
            jsonvalue = params.content[indexstart+1:indexstop]
            try:
                jsondata = json.loads(jsonvalue)
                searchcount = str(jsondata['search_count'])    
            except:
                Logger.getlogging().warning('{}:30000 No comments'.format(params.originalurl))
                return
            if ',' in searchcount:
                searchcount = searchcount.replace(',','')
            if int(searchcount) == 0:
                return
            pagecount = jsondata['page_count']

            #获取第一页搜索结果数据
            self.pageprocess(params)
            if int(pagecount) == 1:
                return
            if int(pagecount) >= self.maxpages:
                pagecount = self.maxpages

            # 根据上面的pagecount数，拼出第一页之外的所有搜索结果url
            info = params.customized['query']
            keyvalue = Common.urlenc(info)
            querylist = []
            for page in range(2, pagecount + 1, 1):
                url = DmzjS2Query.QUERY_TEMPLATE.format(key=keyvalue, pageno=page)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, DmzjS2Query.S2QUERY_EACH_PAGE, {'query': info})
        
            

            
        
        
        
        
        
        
        
        
    
    