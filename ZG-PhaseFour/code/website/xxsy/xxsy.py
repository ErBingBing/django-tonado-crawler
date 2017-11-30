# coding=utf8
from website.common.site import WebSite
from website.xxsy.xxsyComments import XxsyComments

class Xxsy(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'xxsy'
        self.pattern = r'^http://\w+\.xxsy\.net.*'
        self.setcommentimpl(XxsyComments())
        return