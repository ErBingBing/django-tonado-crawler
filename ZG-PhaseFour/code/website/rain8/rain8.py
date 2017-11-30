# coding=utf8
from website.common.site import WebSite
from website.rain8.rain8Comments import Rain8Comments

class Rain8(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'rain8'
        self.pattern = r'^http://\w+\.rain8\.com.*'
        self.setcommentimpl(Rain8Comments())
        return