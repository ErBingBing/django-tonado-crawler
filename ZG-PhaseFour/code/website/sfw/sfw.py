# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import changyanComments

class Sfw(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.sfw\.cn.*'
        self.setcommentimpl(changyanComments())