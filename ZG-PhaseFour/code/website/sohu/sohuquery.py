# -*- coding: utf-8 -*-
################################################################################################################
# @file: sohuquery.py
# @author: JiangSiwei
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from utility.common import Common
from utility.fileutil import FileUtility
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
import re
from  lxml import etree
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, CHARSET_UTF8
from  bs4 import BeautifulSoup 
from configuration import constant
################################################################################################################
# @class：sohuquery
# @author：JiangSiwei
# @date：2016/11/22
# @note：
################################################################################################################
class SohuS2Query(SiteS2Query):
    limit = 50
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SohuS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://video.sohu.com/'
        self.QUERY_TEMPLATE = 'http://so.tv.sohu.com/mts?wd={key}&flag={flag}&c={c}&length={length}&v={v}&limit={limit}&p={page}&o={o}'
        self.DEFAULT_PAGE_SIZE = 20 
        self.S2QUERY_DEFAULT = 'S2QUERY_ORIGINAL_PAGE'
        self.S2QUERY_FIRST_PAGE = 'S2QUERY_FIRST_PAGE'
        self.S2QUERY_EACH_PAGE = 'S2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        key = Common.urlenc(info)
        urls = [self.QUERY_TEMPLATE.format(key=key,flag=0,c=0,length=0,v=0,limit=self.querylastdays,page=1,o=3)]
        self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'key':key,'pages_num':0})

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
            if params.step == self.S2QUERY_FIRST_PAGE:
                self.step1(params)
            if params.step == self.S2QUERY_EACH_PAGE:
                self.step2(params)             
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self,params):
        """
                    step1 检查标签//*[@class="ssPages area"]/span是否存在，判断是否有搜索结果哦
                          step1.1 如果标签span存在，获取//*[@class="ssPages area"]/a的页面数序列pages,判断搜索结果是否只有一页哦
                                  step1.1.1 如果len(pages)>0,
                                            如果len(pages)<=9,则表示搜索结果页面最多只有9页，根据页面情况不需要进行循环找到最大页，此时page_number=pages[-2]
                                                                进行step2获取结果链接，此时通过设置step=self.S2QUERY_EACH_PAGE
                                            如果len(pages) >9,则需要先设置成page_number=pages[-2]最大页，拼出最大页url，进入最大页所在网页后在查看页面序列数len(pages)，
                                                                重复步骤step1,此时通过设置step=self.S2QUERY_FIRST_PAGE
                                  step1.1.2 如果len(pages)==0,则page_number=1
                          step1.2 如果span不存在，则返回
        """
        key = params.customized['key']
        xhtml = etree.HTML(params.content)
        mark_num = 9   
        mark_text = '下一页'
        span = xhtml.xpath('//*[@class="ssPages area"]/span/text()')
        if span:
            pages = xhtml.xpath('//*[@class="ssPages area"]/a/text()') 
            if len(pages)>0:
                #如果获取的列表长度小于等于9，表示最多只有9页，不需要进行下一次循环；否则需要进入重复本页面循环遍历直到获取的列表小于等于9
                if len(pages) <= mark_num:
                    #if pages[-1] == mark_text.encode('utf-8') or pages[-1] == mark_text:
                    if re.search('下一页',''.join(pages)) or re.search(u'下一页',''.join(pages)):
                        page_num = pages[-2]
                    else:
                        page_num = pages[-1]
                    urllist = []
                    for page in range(1,int(page_num)+1):
                        urllist.append(self.QUERY_TEMPLATE.format(key=key,flag=0,c=0,length=0,v=0,limit=self.querylastdays,page=page,o=3))
                    self.__storeqeuryurllist__(urllist, self.S2QUERY_EACH_PAGE, {'key':key})    
                else: 
                    #进入本页面循坏
                    page_num = pages[-2]
                    urls = [self.QUERY_TEMPLATE.format(key=key,flag=0,c=0,length=0,v=0,limit=self.querylastdays,page=page_num,o=3)]
                    self.__storeqeuryurllist__(urls, self.S2QUERY_FIRST_PAGE, {'key':key})             
            else:
                page_num =1
                urls = [self.QUERY_TEMPLATE.format(key=key,flag=0,c=0,length=0,v=0,limit=self.querylastdays,page=page_num,o=3)]
                self.__storeqeuryurllist__(urls, self.S2QUERY_EACH_PAGE, {'key':key})
        else:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return        
    #----------------------------------------------------------------------
    def step2(self,params):
        """解析每一页面"""
        key = Common.urldec(params.customized['key'])
        lt_titles = re.findall('<strong class=\"lt-title\">[\s\S]+?</strong>',params.content)
        urllist = []
        if lt_titles:
            for item in lt_titles:
                if key.encode('utf-8') in item:
                    href = re.findall('href=\"(.+?)\"',item)[0]
                    title = re.findall('title=\"(.+?)\"',item)[0]
                    urllist.append('http:'+href)
            if len(urllist) > 0:       
                self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_VIDEO)
 
    