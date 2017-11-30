# coding=utf8
from website.common.site import WebSite
from website.cn21.Cn21Comments import Comments
from website.common.basicinfo import SiteBasicInfo
 
class Cn21(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '21CN'
        self.pattern = '^http://\w+\.21cn\.com/*'
        #self.setcommentimpl(Comments())