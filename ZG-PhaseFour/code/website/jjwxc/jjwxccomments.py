# -*- coding: utf-8 -*-
################################################################################################################
# @file: Jinjiangyccomments.py
# @author: HuBorui
# @date:  2016/12/05
# @version: Ver0.0.0.100
# @note:
################################################################################################################
from website.jjwxc.jjwxcbbscomments import JjwxcBbsComments
from website.jjwxc.jjwxcnewscomments import JjwxcNewsComments
from website.common.comments import SiteComments
from log.spiderlog import Logger

################################################################################################################
# @class：JjwxcComments
# @author: HuBorui
# @date:  2016/12/05
# @note：
################################################################################################################
class JjwxcComments(SiteComments):


    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：JinjiangycComments，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.news = None
        self.bbs = None


    def createobject(self):
        if self.news is None:
            self.news = JjwxcNewsComments(self)
        if self.bbs is None:
            self.bbs = JjwxcBbsComments(self)


    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteComments， process S1 comments result
    ################################################################################################################
    def process(self, params):
        # 初始化内部子类对象
        self.createobject()
        
        # 1. 根据输入原始url, 得到网站的子域名
        field = self.r.parse('^http[s]{0,1}://(.*)\.jjwxc\.net/.*', params.originalurl)[0]
        if params.step is None:
            # 论坛
            if field == 'bbs':
                self.bbs.bbs_step2(params)
            # 新闻网页
            else:
                self.news.news_step1(params)

        if params.step == JjwxcNewsComments.NEWS_FIRST_PAGE:
            self.news.news_step2(params)

        elif params.step == JjwxcBbsComments.BBS_NEXT_PAGE:
            self.bbs.bbs_step3(params)

        else:
            Logger.getlogging().error(params.step)