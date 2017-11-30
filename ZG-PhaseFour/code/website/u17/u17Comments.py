# -*- coding: utf-8 -*-
##############################################################################################
# @file：U17Comments.py
# @author：Liuyonglin
# @date：2016/12/08
# @version：Ver0.0.0.100
# @note：有妖气获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/19
# @note:原取bbs代码取评论是加上了正文，现在调用公共模板bbs2commom.CommenComments
###############################################################################################
from website.u17.u17NewsComments import U17NewsComments
from website.common.comments import SiteComments
from utility.bbs2commom import CommenComments

##############################################################################################
# @class：xinhuaComments
# @author：Liuyonglin
# @date：2016/12/08
# @note：新华网获取评论的类，继承于SiteComments类
##############################################################################################
class U17Comments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.u17News = None
        self.u17Bbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.u17News is None:
            self.u17News = U17NewsComments(self)
        if self.u17Bbs is None:
            self.u17Bbs = CommenComments(self)

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：none
    ################################################################################################################
    def process(self, params):
        # 初始化内部子类对象
        self.createobject()
        # 论坛评论取得
        if self.r.match('http://bbs.u17.com/.*', params.originalurl):
            self.u17Bbs.process(params)
        #新闻评论取得
        elif self.r.match('http://www.u17.com/.*', params.originalurl):
            self.u17News.process(params)
