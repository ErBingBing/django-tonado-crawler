# coding=utf8
from website.common.site import WebSite
from website.laohu.laohucomments import LaohuComments_all
from website.laohu.laohuquery import LaohuS2Query
from website.laohu.laohupostcomments import LaohuPostComments
from utility.bbs2commom import CommenComments


class Laohu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.laohu\.com/.*'
        # self.setcommentimpl(LaohuComments_all())
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(LaohuS2Query())
        return