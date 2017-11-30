# -*- coding: utf-8 -*-
##############################################################################################
# @file：ptbuscomments.py
# @author：Yangming
# @date：2016/12/15
# @version：Ver0.0.0.100
# @note：口袋巴士获取评论的文件
###############################################################################################
from website.ptbus.ptbusnewscomments import PtbusNewsComments
from website.common.comments import SiteComments
from utility.bbs2commom import CommenComments
from website.common.changyanComments import ChangyanComments


##############################################################################################
# @class：ptbusComments
# @author：Yangming
# @date：2016/12/15
# @note：口袋巴士获取评论的类，继承于SiteComments类
##############################################################################################
class PtbusComments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.ptbusNews = None
        self.ptbusBbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.ptbusNews is None:
            self.ptbusNews = PtbusNewsComments(self)
        if self.ptbusBbs is None:
            self.ptbusBbs = CommenComments(self)

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
        if self.r.match('http://bbs\.ptbus\.com/.*', params.originalurl):
            self.ptbusBbs.process(params)
        # 新闻评论取得
        elif self.r.match('http://.+\.ptbus\.com/.*', params.originalurl):
            # self.ptbusNews.process(params)
            # 非bbs页面评论改为畅言模式，调用畅言模块
            ChangyanComments(self).process(params)
