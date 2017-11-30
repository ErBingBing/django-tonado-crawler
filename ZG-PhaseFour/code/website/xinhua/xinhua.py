# coding=utf8
from website.common.site import WebSite
from website.xinhua.xinhuaComments import xinhuaComments
from website.xinhua.xinhuaquery import xinhuaS2Query

class Xinhua(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.patterns = [];
        self.addpattern(r'^http://.*\.xinhuanet\.com/.*')
        self.addpattern(r'^http://.*\.home\.news\.cn/.*')
        self.setcommentimpl(xinhuaComments())
        self.sets2queryimpl(xinhuaS2Query())
        return