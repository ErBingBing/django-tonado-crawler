# coding=utf8
from website.common.site import WebSite
from website.cine107.cine107comments import Cine107Comments
from website.common.basicinfo import SiteBasicInfo
from website.cine107.cine107query import Cine107S2Query

class Cine107(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '107cine'
        self.pattern = '^http://107cine\.com\/.*'
        self.setcommentimpl(Cine107Comments())
        self.sets2queryimpl(Cine107S2Query())
        return