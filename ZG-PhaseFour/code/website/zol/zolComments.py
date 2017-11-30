# -*- coding: utf-8 -*-
##############################################################################################
# @file：ZolComments.py
# @author：Liuyonglin
# @date：2016/12/09
# @version：Ver0.0.0.100
# @note：中关村获取评论的文件
###############################################################################################
from website.zol.zolbbsComments import ZolbbsComments
from website.zol.zolnewsComments import ZolnewsComments
from website.common.comments import SiteComments

##############################################################################################
# @class：ZolComments
# @author：Liuyonglin
# @date：2016/12/09
# @note：中关村获取评论的类，继承于SiteComments类
##############################################################################################
class ZolComments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.zolNews = None
        self.zolBbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.zolNews is None:
            self.zolNews = ZolnewsComments(self)
        if self.zolBbs is None:
            self.zolBbs = ZolbbsComments(self)

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
        if self.r.match('http://bbs.zol.com.cn/.*', params.originalurl):
            self.zolBbs.process(params)
        #新闻评论取得
        else:
            self.zolNews.process(params)
