# coding=utf8
from website.common.site import WebSite
from website.hupu.hupuquery import hupuS2Query
from website.hupu.hupuComments import hupuComments

class hupu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^https?://(my)?(bbs)?\.hupu\.com/.*'
        self.setcommentimpl(hupuComments())
        self.sets2queryimpl(hupuS2Query())
        return