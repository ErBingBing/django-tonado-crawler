# coding=utf8
from website.common.site import WebSite
from website.zhulang.zhulangComments import zhulangComments

class zhulang(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'zhulang'
        self.pattern = r'^http://www\.zhulang\.com\/.*'
        self.setcommentimpl(zhulangComments())
        return