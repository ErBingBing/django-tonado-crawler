# encoding=utf8
from website.common.site import WebSite

class manshen(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'manshen'
        self.pattern = r'^http://www\.manshen\.net/\w+'
