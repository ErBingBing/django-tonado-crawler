# coding=utf8
from website.common.site import WebSite
from website.adquan.adquanComments import AdquanComments



class Adquan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'adquan'
        self.pattern = r'^http://creative\.adquan\.com/.*'
        self.setcommentimpl(AdquanComments())