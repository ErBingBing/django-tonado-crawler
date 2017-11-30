# -*- coding: utf-8 -*-
################################################################################################################
# @file: tianyaquery.py
# @author: JiangSiwei
# @date:  2016/11/29
# @version: Ver0.0.0.100
# @note: 
# @modify
# @author:Jiangsiwei
# @date:2017/01/13
# @note:119-120代码限定了只能7天，修改后调用self.querylastday
# @date:2017/02/08
# @note:注释掉第92行,使用第91行；第110行添加了对没有查询的urllist时的处理；129行调用了异常处理模块打印输出到日志；124-125添加了标题匹配
# @date:2017/02/10
# @note:第112行判断条件不充分，加强条件
################################################################################################################
from utility.common import Common
from website.common.s2query import SiteS2Query
from utility.gettimeutil import getuniformtime,compareNow
from log.spiderlog import Logger
import traceback
from lxml import etree
from bs4 import BeautifulSoup
import datetime,time
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA

################################################################################################################
# @class：tianyaquery
# @author：JiangSiwei
# @date：2016/11/29
# @note：
################################################################################################################
class TianyaS2Query(SiteS2Query):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SohuS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://search.tianya.cn/bbs?'
        self.QUERY_TEMPLATE = 'http://search.tianya.cn/bbs?q={key}&pn={page}&s=6&f=3'
        self.DEFAULT_PAGE_SIZE = 75
        self.DAYS = 7
        
        self.S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
        self.S2QUERY_SECOND_PAGE = 'S2QUERY_SECOND_PAGE'
        self.S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls1 = [self.QUERY_TEMPLATE.format(key = q,page = 1,new = 4)]
        self.__storeqeuryurllist__(urls1,self.S2QUERY_FIRST_PAGE, {'key':q})    
        
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################    
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        if params.step == self.S2QUERY_FIRST_PAGE:
            self.step1(params)
        if params.step == self.S2QUERY_EACH_PAGE:
            self.step2(params)

    ################################################################################################################
    # @functions：step1
    # @params： params
    # @return：none
    # @note：获取ses关键字，来源于session
    ################################################################################################################         
    #----------------------------------------------------------------------
    def step1(self,params):
        """获取ses关键字,并拼接出要搜索的页面序列"""
        key = params.customized['key']
        xhtml = etree.HTML(params.content)
        if xhtml.xpath('//*[@class="long-pages"]/a/text()'):
            page_num = xhtml.xpath('//*[@class="long-pages"]/a/text()')[-2]
        else:
            page_num = 1
        urllist = []
        for page in range(1,int(page_num)+1):
            url = self.QUERY_TEMPLATE.format(key = key,page = page)
            urllist.append(url)
        self.__storeqeuryurllist__(urllist,self.S2QUERY_EACH_PAGE,{'key':key})    
        
    ################################################################################################################
    # @functions：step2_ac
    # @params： params
    # @return：none
    # @note：通过解析每一页面，获取链接 
    ################################################################################################################    
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""  
        try:
            key = params.customized['key']
            soup = BeautifulSoup(params.content,'html5lib')
            #print soup
            #searchListOne = soup.select('.searchListOne > ul')
            searchListOne = soup.select('.searchListOne > ul > li > div')
            if not searchListOne:
                Logger.getlogging().warning('{}:40000 No urllist'.format(params.originalurl))
                return
            lis = soup.select('.searchListOne > ul > li')[:-1]    #最后一个<li id=search_msg style="display:none"></li>，过滤掉
            urllist = []
            for li in lis:
                url = li.select_one('h3 > a').get('href')
                #print '*********',url
                tm = li.select('.source > span')[0].get_text()
                tm = getuniformtime(tm)
                now = getuniformtime(str(time.time()))
                cmt_num = li.select('.source > span')[-1].get_text()

                title = li.select_one('h3').get_text()
                if Common.checktitle(Common.urldec(key), title):
                    if compareNow(tm,self.querylastdays):
                        urllist.append(url)
            if len(urllist) > 0:
                self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_TIEBA)            
        except:
            #traceback.print_exc()
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))          
  
           
