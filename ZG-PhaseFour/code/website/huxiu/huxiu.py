# coding=utf8
from website.common.site import WebSite
#from website.huxiu.huxiuComments import huxiuComments
from website.huxiu.huxiupostcomments import HuxiupostComments
#from website.common.basicinfo import SiteBasicInfo
class huxiu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'huxiu'
        self.pattern = '^https://www\.huxiu\.com/*'
        self.setcommentimpl(HuxiupostComments())