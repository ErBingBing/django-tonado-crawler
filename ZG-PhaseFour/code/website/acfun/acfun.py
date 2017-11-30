# encoding=utf8
from website.common.site import WebSite
from website.acfun.acfuncomments import AcfunComments
from website.acfun.acfunquery import S2Query

class AcFun(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'acfun'
        self.pattern = r'^http[s]{0,1}://www\.acfun\.cn/v/.*'
        self.setcommentimpl(AcfunComments())
        self.sets2queryimpl(S2Query())
        return