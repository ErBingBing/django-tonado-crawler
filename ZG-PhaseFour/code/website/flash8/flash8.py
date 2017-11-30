# coding=utf8
from website.common.site import WebSite
from website.flash8.flash8Comments import Flash8Comments



class Flash8(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'flash8'
        self.pattern = r'^http://www\.flash8\.net\/*'
        self.setcommentimpl(Flash8Comments())