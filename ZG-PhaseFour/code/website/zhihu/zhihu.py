# coding=utf8
from website.common.site import WebSite
from website.zhihu.zhihucomments import ZhihuComments


class Zhihu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'zhihu'
        self.pattern = r'^https://www\.zhihu\.com/.*'
        self.setcommentimpl(ZhihuComments())
