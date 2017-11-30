# coding=utf8
from website.common.site import WebSite
from website.sougou.sougouNewsComments import SougouNewsComments

class Sougou(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'sougou'
        self.pattern = r'^http[s]{0,1}://kan\.sogou\.com.*'
        self.setcommentimpl(SougouNewsComments())