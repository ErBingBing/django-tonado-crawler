# encoding=utf8
from website.common.site import WebSite
from website.pptv.pptvcomments import PptvComments
from website.pptv.pptvquery import S2Query

class Pptv(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'pptv'
        self.pattern = r'^http://.*\.pptv\.com/.*'
        self.setcommentimpl(PptvComments())
        self.sets2queryimpl(S2Query())
        return