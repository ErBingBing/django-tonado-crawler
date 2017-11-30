# encoding=utf8

##############################################################################################
# @file：dm123comments.py
# @author：Merlin.W.ouyang
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：动漫FANS获取评论的文件
##############################################################################################

import json
import math
import datetime
import traceback
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from utility.xpathutil import XPathUtility
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from storage.urlsstorage import URLCommentInfo
from lxml import etree

##############################################################################################
# @class：dm123Comments
# @author：Merlin.W.ouyang
# @date：2016/12/2
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class Dm123BbsComments(SiteComments):
    COMMENT_URL ='http://bbs.dm123.cn/read-htm-tid-{page}.html'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.ouyang
    # @date：2016/12/2
    # @note：构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    # @author：Merlin.W.ouyang
    # @date：2016/12/2
    # @note：Step1：通过共通模块传入的html内容获取到key,生成当前页数和总页数，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is Dm123BbsComments.STEP_1:
                xparser = XPathUtility(params.content)
                #通过第一次传进来的URL判断是否有后续页面
                keyvalue=self.r.parse('tid-(.*?).html',params.url)[0]
                pagecount = xparser.getnumber('//*[@class="pages"]/div[@class="fl"]')
                commentinfo_url = params.url
                self.storeurl(commentinfo_url, params.originalurl, Dm123BbsComments.STEP_2,
                              {'keyvalue':keyvalue,
                               'totalpage':pagecount,
                               'curpage':1})

            elif params.step == Dm123BbsComments.STEP_2:
                keyvalue =params.customized['keyvalue']
                curpage = params.customized['curpage']
                xparser = XPathUtility(params.content)
                commentsinfo = xparser.getcomments('//div[contains(@class,"tpc_content")]')
                commentstime = self.r.parse(ur'\"(\d+-\d+-\d+ \d+:\d+)\">发表于:', params.content)
                comments = []
                for index in range(0, len(commentstime)):
                    cmti = CommentInfo()
                    if URLStorage.storeupdatetime(params.originalurl,
                                                  TimeUtility.getuniformtime(commentstime[0] + ':00')):
                        # 获取增加的评论（根据时间比较）
                        cmti.content = commentsinfo[index]
                        comments.append(cmti)
                if len(comments) > 0:
                    self.commentstorage.store(params.originalurl, comments)
                nextpageList = [keyvalue, "-page-", str(curpage+ 1)]
                nextpage = ''
                nextpage = nextpage.join(nextpageList)
                if int(nextpageList[2]) <= int(params.customized['totalpage']):
                    comment_url = Dm123BbsComments.COMMENT_URL.format(page=nextpage)
                    self.storeurl(comment_url, params.originalurl, Dm123BbsComments.STEP_2,
                                  {'keyvalue': nextpageList[0],
                                   'totalpage': params.customized['totalpage'],
                                   'curpage': curpage + 1})

        except Exception,e:
            traceback.print_exc()

