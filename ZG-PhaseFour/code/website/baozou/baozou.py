# coding=utf-8
##############################################################################################
# @file：baozou.py
# @author：Han Luyang
# @date：2017/09/11
# @note：暴走漫画网站配置
###############################################################################################
from website.common.site import WebSite
from website.baozou.baozoucomments import BaozouComments
from website.baozou.baozouquery import BaoZouS2Query

##############################################################################################
# @class：BaoZou
# @author：Han Luyang
# @date：2017/09/11
# @note：暴走漫画类
###############################################################################################
class BaoZou(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'baozou'
        self.pattern = r'^http://baozou\.com.*'
        self.setcommentimpl(BaozouComments())
        self.sets2queryimpl(BaoZouS2Query())