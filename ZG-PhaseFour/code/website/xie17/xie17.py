# coding=utf8
from website.common.site import WebSite
from website.xie17.xie17NewsComments import Xie17NewsComments

class Xie17(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'xie17'
        self.pattern = r'^http://xiaoshuo\.17xie\.com\/.*'
        self.setcommentimpl(Xie17NewsComments())
        return