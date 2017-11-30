# coding=utf-8
##############################################################################################
# @file：appgamecomments.py
# @author：Han Luyang
# @date：2017/09/11
# @note：任玩堂论坛页获取评论的文件
##############################################################r################################
import math
import re
from bs4 import BeautifulSoup as bs

from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import getuniformtime
##############################################################################################
# @class：AppgameComments
# @author：Han Luyang
# @date：2017/09/11
# @note：任玩堂论坛页获取评论的类，继承于SiteComments类
##############################################################################################
class AppgameComments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：AppgameComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.reBaseUrl = '^http://www.appgame.com/\w+/\d+\.html'        
        self.commentUrl = 'http://comment.appgame.com/api/comment.php?cmtx_page={page}&page_name={name}&page_id={url}'
        self.page_size = 10.0
        self.STEP_COUNT = None
        self.STEP_PAGES = 1
        self.STEP_CMTS = 2
        
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：step0. 由于basicInfo无法正确解析cmts_count；需要在此手动添加解析
    #        step1. 解析页面，存储评论数；根据评论数，产生分页url，并传递给共通模块 
    #        step2. 解析分页，存储评论信息
    ##############################################################################################
    def process(self, params):
        try:
            if params.step == self.STEP_COUNT:
                self.step0(params)
            if params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_CMTS:
                self.step2(params)
        except:
            Logger.printexception()
    
    ##############################################################################################
    # @functions：step0
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Han Luyang
    # @date：2017/09/11
    # @note: 由于basicInfo无法正确解析cmts_count；需要在此手动添加解析
    ##############################################################################################    
    def step0(self, params):
        try:
            url = params.originalurl
            soup = bs(params.content,'html5lib')
            name = soup.select('h1.appgame-single-title')[0].string.strip()
            page = 1
            baseUrl = self.commentUrl.format(page = page, name = name, url = url)
            self.storeurl(baseUrl, url, step = self.STEP_PAGES, others = {'name':name})
        except:
            Logger.printexception()
    
    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析页面，存储评论数；根据评论数，产生分页url，并传递给共通模块 
    ##############################################################################################
    def step1(self, params):
        try:
            url = params.originalurl
            name = params.customized['name']
            
            soup = bs(params.content,'html5lib')
            # 是否有评论
            currCmtsCount = soup.select('span.cmtx_comments_count')
            currCmtsCount= currCmtsCount[0].string.strip()
            if not currCmtsCount:
                return
            currCmtsCount = int(re.findall('\d+',currCmtsCount)[0])
            NewsStorage.setcmtnum(url, currCmtsCount)
            prevCmtsCount = int(CMTStorage.getcount(url))
            if prevCmtsCount >= currCmtsCount:
                return
            diffPageNum = int(math.ceil((currCmtsCount - prevCmtsCount) / self.page_size))
            for page in range(1, diffPageNum + 1):
                pageurl = self.commentUrl.format(page = page, name = name, url = url)
                self.storeurl(pageurl, url, self.STEP_CMTS)
        except:
            Logger.printexception()
   
    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析分页，存储评论信息
    ##############################################################################################
    def step2(self, params):
        soup = bs(params.content,'html5lib')
        cmtsContainer = soup.select('div.comment_box_wrapper')
        for cmtContainer in cmtsContainer:
            try:
                content = cmtContainer.select_one('span.cmtx_comment_text').get_text()
                pubDate = cmtContainer.select_one('div.cmtx_date_text').get_text()
                user = ''
                CMTStorage.storecmt(params.originalurl, content, pubDate, user)
            except:
                Logger.printexception()
