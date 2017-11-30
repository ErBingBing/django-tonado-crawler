# coding=utf8
from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.pk52.pk52query import PK52S2Query

class PK52(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '52pk'
        self.pattern = r'http[s]{0,1}://.*\.52pk\.com.*'
        self.setcommentimpl(CommenComments())
        #self.setcommentimpl(Pk52Comments())
        self.sets2queryimpl(PK52S2Query())
        return