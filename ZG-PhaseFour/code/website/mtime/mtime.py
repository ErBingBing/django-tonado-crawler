# coding=utf8
from website.common.site import WebSite
from website.mtime.mtimeComments import MtimeComments

class Mtime(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'mtime'
        self.pattern = r'^http[s]?://.*\.mtime\.com.*'
        self.setcommentimpl(MtimeComments())
        return