# -*- coding: utf-8 -*-
################################################################################################################
# @file: Dmzjcomments.py
# @author: HuBorui
# @date:  2016/12/05
# @version: Ver0.0.0.100
# @note:
################################################################################################################
from website.dmzj.dmzjnewscomments import DmzjNewscomments
from website.dmzj.dmzjvideocomments import DmzjVideocomments
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.bbs2commom import CommenComments 
from configuration import constant 
################################################################################################################
# @class：DmzjComments
# @author: HuBorui
# @date:  2016/12/05
# @note：
################################################################################################################
class DmzjComments(SiteComments):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：DmzjComments，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteComments， process S1 comments result
    ################################################################################################################
    def process(self, params):
        # 初始化内部子类对象
        field = ''
        # 1. 根据输入原始url, 得到网站的子域名
        if self.r.match('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl):
            field = self.r.parse('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl)[0]
        else:
            field = self.r.parse('^http[s]{0,1}://(\w+).dmzj.com/.*', params.originalurl)[0]
        if not field:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_TEMPLATE)

        if field == 'bbs':
            CommenComments(self).process(params)       
        # elif field == 'news' or field == 'manhua' or field == 'xs' or field == 'info':
        #     DmzjNewscomments(self).process(params)
        else:
            DmzjNewscomments(self).process(params)
