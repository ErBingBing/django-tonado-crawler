# coding=utf8
from website.common.site import WebSite
from website.tadu.taduComments import TaDuComments

class TaDu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tadu'
        self.pattern = r'^http://\w+\.tadu\.com/.*'
        self.setcommentimpl(TaDuComments())
        return