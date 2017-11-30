# coding=utf8
from website.common.site import WebSite
from website.kkk1.kkkManhuaComments import kkkManhuaComments

class kkkManhua(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '1kkk'
        self.pattern = r'^http://www\.1kkk\.com/.*'
        self.setcommentimpl(kkkManhuaComments())
        return