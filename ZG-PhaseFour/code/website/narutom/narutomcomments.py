# -*- coding: utf-8 -*-
##############################################################################################
# @file：narutomComments.py
# @author：Liyanrui
# @date：2016/12/8
# @version：Ver0.0.0.100
# @note：火影忍者获取评论的文件
###############################################################################################
from utility.bbs2commom import CommenComments
from website.narutom.narutomvideocomments import NarutomVideoComments
from website.common.comments import SiteComments

##############################################################################################
# @class：NarutomComments
# @author：Liyanrui
# @date：2016/12/8
# @note：火影忍者获取评论的类，继承于SiteComments类
##############################################################################################
class NarutomComments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.narutomVideo = None
        self.narutomBbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：none
    ################################################################################################################
    def createobject(self):
        if self.narutomVideo is None:
            self.narutomVideo = NarutomVideoComments(self)
        if self.narutomBbs is None:
            self.narutomBbs = CommenComments(self)

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
        if self.r.match('http://bbs\.narutom\.com\/*', params.originalurl):
            self.narutomBbs.process(params)
        # 视频评论取得
        else:
            self.narutomVideo.process(params)
