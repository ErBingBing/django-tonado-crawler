# encoding=utf-8
##############################################################################################
# @file：doubanComments.py
# @author：Liyanrui
# @date：2016/11/17
# @version：Ver0.0.0.100
# @note：豆瓣电影选“电影”获取评论的文件
###############################################################################################
import re
import urllib
import json
import math
from utility.timeutility import TimeUtility
from utility.common import Common
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup

##############################################################################################
# @class：doubanComments
# @author：Liyanrui
# @date：2016/11/17
# @note：豆瓣电影选“电影”获取评论的类，继承于SiteComments类
##############################################################################################
class doubanComments(SiteComments):
    COMMENTS_URL = 'https://movie.douban.com/subject/{articleId}/comments?start={start}&limit={pagesize}&sort=new_score&status=P'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    Flg = True

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/17
    # @note：豆瓣电影选“电影”类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is self.STEP_1:
                self.step1(params)
            elif params.step == self.STEP_2:
                self.step2(params)
        except:
            Logger.printexception()	
    
    #----------------------------------------------------------------------
    def step1(self, params):
        # 取得url中的id
        articleId = self.r.parse(r'^https://movie\.douban\.com/\w+/(\d+)', params.url)[0]
        # 取得评论件数
        xpathobj = XPathUtility(params.content)
        text = xpathobj.getstring(xpath='//*[@id="comments-section"]//h2/*[@class="pl"]/a')
        numtext = self.r.parse('\d+', text)
        if not numtext:
            return 
        curcmtnum = float(numtext[0])
        NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        if dbcmtnum >= curcmtnum:
            return    
        # 循环取得评论的url
        pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGE_SIZE))
        if pages >= self.maxpages:
            pages = self.maxpages
        for page in range(1, pages + 1, 1):
            url = doubanComments.COMMENTS_URL.format(articleId=articleId, start=(page-1) * self.PAGE_SIZE, pagesize=self.PAGE_SIZE)
            self.storeurl(url, params.originalurl, doubanComments.STEP_2)
        
    #----------------------------------------------------------------------
    def step2(self, params):
        # 取得评论
        soup = BeautifulSoup(params.content, 'html5lib')
        comments = soup.select('#comments > .comment-item')
        for comment in comments:
            try:
                curtime = comment.select_one('.comment-time').get('title')   
                content = comment.select_one('.comment > p').get_text() 
                CMTStorage.storecmt(params.originalurl, content, curtime, '')
            except:
                Logger.printexception()        