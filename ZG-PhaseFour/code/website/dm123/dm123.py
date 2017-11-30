# coding=utf8
from website.common.site import WebSite
from website.dm123.dm123Comments import Dm123Comments



class Dm123(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'dm123'
        self.pattern = r'^http://.*\.dm123\.cn/.*'
        self.setcommentimpl(Dm123Comments())