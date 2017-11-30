# coding=utf8
from website.common.site import WebSite
from website.leiphone.leiphonecomments import LeiphoneComments

class Leiphone(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http[s]?://www\.leiphone\.com/.*'
        self.setcommentimpl(LeiphoneComments())
        return