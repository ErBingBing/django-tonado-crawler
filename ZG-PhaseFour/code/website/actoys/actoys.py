# -*- coding: utf-8 -*-
###################################################################################################
# @file: actoys.py
# @author: Han Luyang
# @date: 2017/09/11
# @note: actoys网站配置
###################################################################################################
from website.common.site import WebSite
from website.actoys.actoyscomments import ActoysComments

###################################################################################################
# @class: Actoys
# @author: Han Luyang
# @date: 2017/09/11
# @note: actoys网站类
###################################################################################################
class Actoys(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'actoys'
        self.pattern = r'^^http://\w+\.actoys.net.*'
        self.setcommentimpl(ActoysComments())