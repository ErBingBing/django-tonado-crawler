# coding=utf8
from website.common.site import WebSite
from website.u17.u17Comments import U17Comments



class U17(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'u17'
        self.pattern = r'^http://.*\.u17\.com/.*'
        self.setcommentimpl(U17Comments())