# coding=utf8
from website.common.site import WebSite
from website.yeyou.yeyoucomments import YeyouComments

class YeYou(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.yeyou\.com.*'
        self.setcommentimpl(YeyouComments())