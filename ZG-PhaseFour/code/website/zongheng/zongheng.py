# coding=utf8
from website.common.site import WebSite
from website.zongheng.zonghengComments import ZongHengComments
from website.common.basicinfo import SiteBasicInfo

class ZongHeng(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'zongheng'
        self.pattern = '^http[s]{0,1}://\w+\.zongheng\.com/*'
        self.setcommentimpl(ZongHengComments())
        return