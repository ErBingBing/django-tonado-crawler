# coding=utf8
from website.common.site import WebSite
from website.maoyan.maoyancomments import MaoYanComments

class MaoYan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'maoyan'
        self.pattern = r'^http://maoyan.com.*'
        self.setcommentimpl(MaoYanComments())