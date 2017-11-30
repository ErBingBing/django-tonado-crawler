# coding=utf8
from website.common.site import WebSite
from website.one7173.one7173comments import One7173Comments
from website.one7173.one7173query import One7173Query

class One7173(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '17173'
        self.pattern = r'^http[s]{0,1}://\w+\.17173\.com/.*'
        self.setcommentimpl(One7173Comments())
        self.sets2queryimpl(One7173Query())