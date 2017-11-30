# coding=utf8
from website.common.site import WebSite
from website.muu.muuNewsComments import muuNewsComments

class muu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'muu'
        self.pattern = r'^http://www\.muu\.com\.cn/.*'
        self.setcommentimpl(muuNewsComments())
        return