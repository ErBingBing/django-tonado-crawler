# coding=utf8
################################################################################################################
# @file：appgame.py
# @author: Han Luyang
# @date: 2017/09/11
# @note： appgame网站配置
################################################################################################################
from website.common.site import WebSite
from website.appgame.appgamecomments import AppgameComments 

################################################################################################################
# @class：Appgame
# @author: Han Luyang
# @date: 2017/09/11
# @note：appgame网站类
################################################################################################################
class Appgame(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'appgame'
        self.pattern = r'^http[s]{0,1}://.*\.appgame\.com/.*'
        self.setcommentimpl(AppgameComments())