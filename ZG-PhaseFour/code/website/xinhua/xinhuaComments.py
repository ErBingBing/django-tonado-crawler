# -*- coding: utf-8 -*-
##############################################################################################
# @file：xinhuaComments.py
# @author：Liyanrui
# @date：2016/11/26
# @version：Ver0.0.0.100
# @note：新华网获取评论的文件
###############################################################################################
from website.xinhua.xinhuaBbsComments import xinhuaBbsComments
from website.xinhua.xinhuaNewsComments import xinhuaNewsComments
from website.common.comments import SiteComments

##############################################################################################
# @class：xinhuaComments
# @author：Liyanrui
# @date：2016/11/26
# @note：新华网获取评论的类，继承于SiteComments类
##############################################################################################
class xinhuaComments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.xinhuaNews = None
        self.xinhuaBbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.xinhuaNews is None:
            self.xinhuaNews = xinhuaNewsComments(self)
        if self.xinhuaBbs is None:
            self.xinhuaBbs = xinhuaBbsComments(self)

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
        if self.r.match('http://forum.home.news.cn/.*', params.originalurl):
            self.xinhuaBbs.process(params)
        #新闻评论取得
        elif self.r.match('http://news\.xinhuanet\.com/.*', params.originalurl):
            self.xinhuaNews.process(params)


