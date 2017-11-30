# encoding=utf8

##############################################################################################
# @file：dm123comments.py
# @author：Merlin.W.ouyang
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：动漫FANS获取评论的文件
##############################################################################################

import traceback
from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from website.dm123.dm123BbsComments import Dm123BbsComments
from website.dm123.dm123NewsComments import Dm123NewsComments

##############################################################################################
# @class：dm123Comments
# @author：Merlin.W.ouyang
# @date：2016/12/2
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class Dm123Comments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.ouyang
    # @date：2016/12/2
    # @note：构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.dm123News = None
        self.dm123Bbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.dm123News is None:
            self.dm123News = Dm123NewsComments(self)
        if self.dm123Bbs is None:
            self.dm123Bbs = Dm123BbsComments(self)

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
            # 初始化内部子类对象
            self.createobject()
            # 论坛评论取得
            if self.r.match('http://bbs.dm123.cn/.*', params.originalurl):
                self.dm123Bbs.process(params)
            # 新闻评论取得
            elif self.r.match('http://www.dm123.cn/.*', params.originalurl):
                self.dm123News.process(params)
        except Exception,e:
            traceback.print_exc()

