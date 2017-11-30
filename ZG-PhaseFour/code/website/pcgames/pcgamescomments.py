# encoding=utf-8
##############################################################################################
# @file：pcgamescomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/26
# @note：78DM评论获取
##############################################################################################

import re
from website.common.comments import SiteComments
from website.pcgames.bbscomments import BBSComments
from website.pcgames.newscomments import NewsComments
from log.spiderlog import Logger
import traceback
import datetime
from lxml import etree
from utility.xpathutil import XPathUtility

##############################################################################################
# @class：PcgamesComments
# @author：Merlin.W.OUYANG
# @date：2016/11/26
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class PcgamesComments(SiteComments):
    COMMENTS_URL = 'http://bbs.pcgames.com.cn/%s.html'
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/26 -> 2016/12/30 by Hedian modified
    # @note：78DM类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.news = None
        self.bbs = None

    ##############################################################################################
    # @functions：createobject
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/12/30
    # @note：创建真正抓取评论的类对象
    ##############################################################################################
    def createobject(self):
        if self.news is None:
            self.news = NewsComments(self)
        if self.bbs is None:
            self.bbs = BBSComments(self)

    ##############################################################################################
    # @functions：process
    # @params：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：none
    # @author：Merlin.W.ouyang
    # @date：2016/11/26 -> 2016/12/30 by Hedian modified
    # @note：根据原始url得到子域名，根据不同的子域名调用不同的类处理
    ##############################################################################################
    def process(self, params):
        self.createobject()
        try:
            # Step1: 通过url得到子域名
            field = self.r.parse('^http[s]{0,1}://(\w+)\.?', params.originalurl)[0]
            params.customized['field'] = field
            if field == 'bbs':
                # 论坛抓取评论处理
                self.bbs.process(params)
            # elif field == 'sy':
            #     # 新闻抓取评论处理
            #     self.news.process(params)
            else:
                # 新闻处理
                self.news.process(params)

        except:
            Logger.printexception()
