# coding=utf8
from website.common.site import WebSite
from website.douban.doubanComments import doubanComments

class douban(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'douban'
        self.pattern = r'^https://movie\.douban\.com/.*'
        self.setcommentimpl(doubanComments())
        return