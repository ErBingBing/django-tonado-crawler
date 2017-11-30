# -*- coding: utf-8 -*-
##############################################################################################
# @file：dm78comments.py
# @author：Liyanrui
# @date：2016/12/10
# @version：Ver0.0.0.100
# @note：78动漫模型玩具获取评论的文件
###############################################################################################
from website.dm78.dm78newscomments import dm78NewsComments
from website.common.comments import SiteComments
from utility.bbs2commom import CommenComments 

##############################################################################################
# @class：dm78Comments
# @author：Liyanrui
# @date：2016/12/10
# @note：78动漫模型玩具获取评论的类，继承于SiteComments类
##############################################################################################
class dm78Comments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.dm78News = None
        self.dm78Bbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：none
    ################################################################################################################
    def createobject(self):
        if self.dm78News is None:
            self.dm78News = dm78NewsComments(self)
        if self.dm78Bbs is None:
            self.dm78Bbs = CommenComments(self)

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
        if self.r.match('http://bbs\.78dm\.net/forum.php.*', params.originalurl):
            self.dm78Bbs.process(params)
        # 新闻评论取得
        else:
            self.dm78News.process(params)
