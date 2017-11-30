# -*- coding: utf-8 -*-
################################################################################################################
# @file: baozouquery.py
# @author: Han Luyang
# @date:  2017/09/11
# @note: 暴走漫画查询处理文件
################################################################################################################
import math
import re
from bs4 import BeautifulSoup as bs

from configuration.constant import SPIDER_S2_WEBSITE_VIDEO, SPIDER_S2_WEBSITE_NEWS
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
################################################################################################################
# @class：BaoZouS2Query
# @author：Han Luyang
# @date：2017/09/11
# @note：暴走漫画查询类
################################################################################################################
class BaoZouS2Query(SiteS2Query):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：BaoZouS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        self.fakeoriginalurl = 'http://baozou.com/'
        self.queryUrl = 'http://zhannei.baidu.com/cse/search?q={keyword}&p={page}&s=8807869111209310469&entry=1'
        self.pageUrl = self.queryUrl
        self.maxPage = 76
        self.pageSize = 10.0
        self.STEP_PAGES = None
        self.STEP_ARTICLES_OR_VIDEOS = 1
        self.reArticle = '^http://baozou\.com/articles/\S*'
        self.reVideo = '^http://baozou\.com/videos/\S*'
        
    ##############################################################################################################
    # @functions：query
    # @param: query关键字
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：共通模块调用，产生query的原始url
    ################################################################################################################
    def query(self, info):
        keyword = Common.urlenc(info)
        urls = [self.queryUrl.format(keyword = keyword, page = 0)]
        self.__storeqeuryurllist__(urls, self.STEP_PAGES, {'keyword':keyword})

    ################################################################################################################
    # @functions：process
    # @params：共通模块参数url，原始url，step及自定义参数
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：step1. 解析query原始页面，产生分页url，向共通模块传递
    #        step2. 解析分页，产生当页的内容url，过滤并向共通模块传递
    ################################################################################################################
    def process(self, params):
        try:
            if params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_ARTICLES_OR_VIDEOS:
                self.step2(params)
        except:
            Logger.printexception()
    
    ################################################################################################################
    # @functions：step1
    # @params：共通模块参数url，原始url，step及自定义参数
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：解析query原始页面，产生分页url，向共通模块传递
    ################################################################################################################    
    def step1(self, params):
        keyword = params.customized['keyword']
        soup = bs(params.content,'html5lib')
        # 是否有结果
        hasResults = soup.select('.support-text-top')
        if not hasResults:
            return
        
        resStr = hasResults[0].string.strip()
        resNum = self._str2num(resStr)
        # 计算分页数
        estPageNum = int(math.ceil(resNum/self.pageSize))
        pageNum = min(estPageNum, self.maxPage)
        
        pageUrlList = []
        # 拼接分页url并传递
        for page in range(0, pageNum):
            pageUrl = self.pageUrl.format(keyword = keyword, page = page)
            pageUrlList.append(pageUrl)
        
        self.__storeqeuryurllist__(pageUrlList, self.STEP_ARTICLES_OR_VIDEOS)
    ################################################################################################################
    # @functions：step2
    # @params：共通模块参数url，原始url，step及自定义参数
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：解析分页，产生当页的内容url，过滤并向共通模块传递
    ################################################################################################################        
    def step2(self, params):
        soup = bs(params.content,'html5lib')
        resUrlsWrapper = soup.find_all(class_='result f s0')
        
        resVideoUrls = []
        resArticleUrls = []
        # 解析分页，产生内容url，过滤只属于article和video的url并传递给共通模块
        for resUrlWrapper in resUrlsWrapper:
            resUrl = resUrlWrapper.a['href'].strip()
            isArticle = re.match(self.reArticle, resUrl)
            isVideo = re.match(self.reVideo, resUrl)
            if isArticle:
                resArticleUrls.append(resUrl)
            if isVideo:
                resVideoUrls.append(resUrl)
        
        self.__storeurllist__(resArticleUrls, type=SPIDER_S2_WEBSITE_NEWS)
        self.__storeurllist__(resVideoUrls)
     
    ################################################################################################################
    # @functions：_str2num
    # @params：包含数字的字符串
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：从字符串解析出数字
    ################################################################################################################        
    def _str2num(self,numStr):
        numStr = numStr.replace(',','')
        patt = '\d+'
        num = int(re.findall(patt,numStr)[0])
        return num
        
            
        
        
                        



