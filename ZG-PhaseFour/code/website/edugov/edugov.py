# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments

class Edugov(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.edu-gov\.cn.*'
        self.setcommentimpl(ChangyanComments())