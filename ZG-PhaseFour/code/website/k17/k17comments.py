# coding=utf-8
##############################################################################################
# @file：k17Comments.py
# @author：Ninghz
# @date：2016/12/7
# @note：17k获取评论的文件
##############################################################################################

import json
import datetime
import traceback
import time
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from utility.bbs2commom import CommenComments
##############################################################################################
# @class：Comments
# @author：Ninghz
# @date：2016/12/7
# @note：17k获取评论的类，继承于SiteComments类
##############################################################################################
class Comments(SiteComments):
    COMMENTS_URL = 'http://comment.17k.com/topic_list?commentType=all&order=1&bookId=%s&page=%d&pagesize=%d'
    PAGE_SIZE = 20.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/12/7
    # @note：Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()
        # self.basicstorage = BaseInfoStorage()
        # self.commentstorage = CommentsStorage()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/09/15
    # @note：Step1：通过共通模块传入的html内容获取到operaId，contentId，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        if self.r.search('http[s]{0,1}://www\.17k\.com.*',params.originalurl):
            self.process_book(params)
        if self.r.search('http[s]{0,1}://bbs\.17k\.com.*',params.originalurl):
            CommenComments(self).process(params)
        
    def process_book(self, params):
        try:
            if params.step == Comments.STEP_1:
                # 从url中获取拼接评论url的参数
                bookId = self.r.parse('^http://www\.17k\.com/book/(\w+).html$', params.originalurl)[0]
                # 拼接第一页评论url
                comments_url = Comments.COMMENTS_URL % (bookId, 1, Comments.PAGE_SIZE)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, Comments.STEP_2, {'bookId':bookId})

            #获取第一页评论内容，循环获取全部评论url
            elif params.step == Comments.STEP_2:
                bookId = params.customized['bookId']
                # 获取评论的Jason返回值
                comments = json.loads(params.content)

                comments_count = int(comments['page']['count'])
                # 判断增量
                cmtnum = CMTStorage.getcount(params.originalurl)
                if cmtnum >= comments_count:
                    return
                NewsStorage.setcmtnum(params.originalurl, comments_count)
                # 获取评论最后更新时间
                lasttime = CMTStorage.getlastpublish(params.originalurl, True)
                # 获取评论页数
                page_count = int(comments['page']['pagecount'])
                if page_count == 0:
                    return

                if page_count >= self.maxpages:
                    page_count = self.maxpages

                # 循环拼接评论url，提交下载平台获取评论数据
                for page in range(1, page_count + 1, 1):
                    commentUrl = Comments.COMMENTS_URL % (bookId, page, Comments.PAGE_SIZE)
                    self.storeurl(commentUrl, params.originalurl, Comments.STEP_3, {'bookId':bookId})

            #解析评论数据
            elif params.step == Comments.STEP_3:
                commentsinfo = json.loads(params.content)

                for comment in commentsinfo['page']['result']:
                    curtime = TimeUtility.getuniformtime(comment['creationDate'])
                    content = comment['summary']
                    nick = comment['marks']['nikeName']
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)

        except Exception, e:
            traceback.print_exc()