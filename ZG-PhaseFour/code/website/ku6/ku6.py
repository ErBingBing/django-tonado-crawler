# coding=utf8
from website.common.site import WebSite
from website.ku6.ku6comments import Ku6Comments
from website.common.basicinfo import SiteBasicInfo
from website.ku6.ku6query import Ku6S2Query

class Ku6(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ku6'
        #self.pattern = '^http://v\.ku6\.com/show/[\w-]+\.{3}html(\?\w+=\w+)?'
        self.pattern = '^http://\w+\.ku6\.com.*'
        #self.comments = ku6Comments()
        #self.basic = SiteBasicInfo()
        self.setcommentimpl(Ku6Comments())
        self.sets2queryimpl(Ku6S2Query())
        return