# coding=utf8
from website.common.site import WebSite
from website.hongxiu.hongxiuComments import HongXiuComments

class HongXiu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'hongxiu'
        self.pattern = r'^http://\w+\.hongxiu\.com.*'
        self.setcommentimpl(HongXiuComments())
        return