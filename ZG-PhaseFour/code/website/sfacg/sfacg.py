# coding=utf8
from website.common.site import WebSite
from website.sfacg.sfacgcomments import SfacgComments

class Sfacg(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'sfacg'
        self.pattern = r'http[s]{0,1}://.*\.sfacg\.com.*'
        self.setcommentimpl(SfacgComments())
        # self.sets2queryimpl(PK52S2Query())
        return