# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments

class yesky(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+.yesky.com.*'
        self.setcommentimpl(ChangyanComments())