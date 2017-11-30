# coding=utf8

from website.common.site import WebSite
from website.ptbus.ptbuscomments import PtbusComments
from website.ptbus.ptbusquery import PtbusS2Query

class Ptbus(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ptbus'
        self.pattern = r'^http[s]{0,1}://.*\.ptbus\.com/.*'
        self.setcommentimpl(PtbusComments())
        self.sets2queryimpl(PtbusS2Query())
        return