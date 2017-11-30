# coding=utf8
from website.common.site import WebSite
from website.mkzhan.mkzhancomments import MkzhanComments

class mkzhan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'mkzhan'
        self.pattern = r'^http[s]?://www\.mkzhan\.com/.*'
        self.setcommentimpl(MkzhanComments())
        return