# coding=utf8
from website.common.site import WebSite
from website.gfan.gfancomments import GfanComments
from website.gfan.gfanQuery import S2Query


class Gfan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gfan'
        self.pattern = r'^http[s]{0,1}://.*\.gfan\.com.*'
        self.setcommentimpl(GfanComments())
        self.sets2queryimpl(S2Query())
        return