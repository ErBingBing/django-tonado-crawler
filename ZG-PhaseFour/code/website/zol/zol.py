# coding=utf8
from website.common.site import WebSite
from website.zol.zolComments import ZolComments
from website.zol.zolbbsquery import ZolBbsS2Query

class Zol(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'zol'
        self.pattern = r'^http://.*\.zol\.com\.cn.*'
        self.setcommentimpl(ZolComments())
        self.sets2queryimpl(ZolBbsS2Query())
        return