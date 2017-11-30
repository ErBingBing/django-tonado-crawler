# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments

class One78(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.178\.com/.*'
        self.setcommentimpl(ChangyanComments())