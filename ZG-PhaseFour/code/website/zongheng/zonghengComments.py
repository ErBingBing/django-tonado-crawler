# encoding=utf-8

##############################################################################################
# @file：zonghengcomments.py
# @author：QW_Liang
# @date：2017/9/16
# @version：Ver0.0.0.100
# @note：纵横小说网获取评论的文件
##############################################################r################################

import json
import math
import re
import datetime
import traceback

from utility.regexutil import RegexUtility
from website.common.site import WebSite
from log.spiderlog import Logger
from website.common.comments import SiteComments
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
from website.zongheng.zonghengBookComments import BookComments
from website.zongheng.zonghengPubComments import PubComments
from website.zongheng.zonghengBbsComments import BbsComments


##############################################################################################
# @class：ZongHengComments
# @author：QW_Liang
# @date：2017/9/16
# @note：纵横小说网获取评论的类，继承于WebSite类
##############################################################################################


class ZongHengComments(SiteComments):
    STEP_1 = None
    STEP_2_BOOK = '2_book'
    STEP_3_BOOK = '3_book'
    STEP_2_PUB = '2_pub'
    STEP_3_PUB = '3_pub'
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：ninghz
    # @date：2016/12/6
    ##############################################################################################

    def __init__(self):
        SiteComments.__init__(self)
        self.book = None
        self.pub = None
        self.bbs = None

    ################################################################################################################
    # @functions：createobject
    # @param： none
    # @return：none
    # @note：初始化实现真正检索的类对象，需要把接口类的self传递给类
    ################################################################################################################
    def createobject(self):
        if self.book is None:
            self.book = BookComments(self)
        if self.pub is None:
            self.pub = PubComments(self)
        if self.bbs is None:
            self.bbs = BbsComments(self)

        ##############################################################################################
        # @functions：process
        # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
        # @return：无
        # @author：ninghz
        # @date：2016/12/6
        # @note：入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
        ##############################################################################################

    def process(self, params):
        # 创建评论对象
        self.createobject()
        try:
            if params.step is ZongHengComments.STEP_1:
                # 1. 根据输入原始url, 获得子域名
                field = self.r.parse('^http://(\w+)\.zongheng\.com*', params.originalurl)[0]
                if field == 'book':
                    # 书库
                    self.book.getcomments_step1(params)
                elif field == 'pub':
                    # 图书
                    self.pub.getcomments_step1(params)
                elif field == 'bbs':
                    # BBS
                    self.bbs.getcomments_step1(params)

            elif params.step == ZongHengComments.STEP_2_BOOK:
                self.book.getcomments_step2(params)

            elif params.step == ZongHengComments.STEP_3_BOOK:
                self.book.getcomments_step3(params)

            elif params.step == ZongHengComments.STEP_2_PUB:
                self.pub.getcomments_step2(params)

            elif params.step == ZongHengComments.STEP_3_PUB:
                self.pub.getcomments_step3(params)

            elif params.step == ZongHengComments.STEP_2_BBS:
                self.bbs.getcomments_step2(params)

            elif params.step == ZongHengComments.STEP_3_BBS:
                self.bbs.getcomments_step3(params)
            else:
                return

        except Exception, e:
            traceback.print_exc()


