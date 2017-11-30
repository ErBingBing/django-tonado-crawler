# coding=utf8
from website.common.site import WebSite
from website.thepaper.thepaperComment import ThepaperComments


class Thepaper(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'thepaper'
        self.pattern = '^http://www\.thepaper\.cn.*'
        self.setcommentimpl(ThepaperComments())