# coding=utf8
from website.common.site import WebSite
from website.le.lecomments import LeComments
from website.le.lequery import LeQuery

class Le(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'le'
        self.pattern = r'^http[s]{0,1}://.*\.le\.com/.*'
        self.setcommentimpl(LeComments())
        self.sets2queryimpl(LeQuery())
        return