# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments

class Yzz(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.yzz\.cn.*'
        self.setcommentimpl(ChangyanComments())