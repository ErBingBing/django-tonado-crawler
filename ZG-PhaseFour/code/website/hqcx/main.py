# encoding=utf8
from website.common.site import WebSite
from website.hqcx.AllComments import AllComments

class hqcx(WebSite):
    def __init__(self):
        WebSite.__init__(self)  
        self.name = 'hqcx'
        self.pattern = r'^http://\www\.hqcx\.net/gncx/\w+/\d{8}/\d+\.html$'
        self.setcommentimpl(AllComments())