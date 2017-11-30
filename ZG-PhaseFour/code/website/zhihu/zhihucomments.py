# -*- coding: utf-8 -*-
##############################################################################################
# @file：zhihucomments.py
# @author：QW_Liang
# @date：2017/09/10
# @version：Ver0.0.0.100
# @note：知乎获取评论的文件
###############################################################################################
import datetime
import traceback
import math
from log.spiderlog import Logger
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from bs4 import BeautifulSoup
import re
from utility.gettimeutil import getuniformtime,compareNow
from configuration import constant 
##############################################################################################
# @class：zhihucomments
# @author：QW_Liang
# @date：2017/09/10
# @note：知乎获取评论的类，继承于SiteComments类
##############################################################################################
class ZhihuComments(SiteComments):
    COMMENTS_URL = 'https://www.zhihu.com/question/%s?sort=created&page=%d'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'
    page_size = 20

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/10
    # @note：ToutiaoComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is ZhihuComments.STEP_1:
                self.step2(params)
                publish = self.r.getid('itemprop="dateCreated" content', params.content, split='=')
                if publish:
                    NewsStorage.setpublishdate(params.originalurl, publish)
            #if params.step is ZhihuComments.STEP_2:
                #self.step2(params)
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/10
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    #def step1(self, params):
        #if not re.search('http[s]{0,1}://www\.zhihu\.com/question/(\d+)',params.originalurl):
            #return
        #comment_id = re.findall('http[s]{0,1}://www\.zhihu\.com/question/(\d+)',params.originalurl)[0]
        # 取得评论个数
        #soup = BeautifulSoup(params.content, 'html5lib')
        #textobj = soup.select_one('.List-headerText')
        #comments_count = 0
        #if textobj:
            #comments_count = self.str2num(textobj.get_text())
        #if not comments_count or not textobj:
            #Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            #return 

        ## 判断增量
        #cmtnum = CMTStorage.getcount(params.originalurl,True)
        #if cmtnum >= comments_count:
            #return
        #NewsStorage.setcmtnum(params.originalurl, comments_count)

        ## 循环取得评论的url
        #page_num = int(math.ceil(float(comments_count - cmtnum) / self.page_size))
        #if page_num >= self.maxpages:
            #page_num = self.maxpages

        #for page in range(1, page_num + 1, 1):
            ## 取得评论的url
            #if page == 1:
                #self.step2(params)
                #continue
            #url = ZhihuComments.COMMENTS_URL % (comment_id, page)
            #self.storeurl(url, params.originalurl, ZhihuComments.STEP_2)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/10
    # @note：根据输入的html，得到评论
    ##############################################################################################
    def step2(self, params):
        try:
            soup = BeautifulSoup(params.content, 'html5lib')
            items = soup.select('.List > div > .List-item')
            if not items:
                return
            for item in items:
                times = item.select_one('.ContentItem-time').get_text()
                content = item.find(attrs={"class":"RichText CopyrightRichText-richText"}).get_text()
                curtime = getuniformtime(times)
                nick = item.select_one('.ContentItem-meta > .AnswerItem-meta > .AuthorInfo').get_text()
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()