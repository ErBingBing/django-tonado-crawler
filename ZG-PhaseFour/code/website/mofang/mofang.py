# coding=utf8

from website.common.site import WebSite
from website.mofang.mofangcomments import MofangComments
from website.mofang.mofangquery import MofangS2Query

class Mofang(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'mofang'
        self.pattern = r'^http[s]{0,1}://.*\.mofang\.com/.*'
        # self.setcommentimpl(MofangComments())
        # self.sets2queryimpl(MofangS2Query())
        return