# coding=utf-8

from website.common.site import WebSite
from website.wangdafilm.wangdafilmcomments import WangdafilmComments

class Wangdafilm(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'wandafilm'
        self.pattern = r'^http[s]{0,1}://.*\.wandafilm\.com/.*'
        self.setcommentimpl(WangdafilmComments())
        return
        

