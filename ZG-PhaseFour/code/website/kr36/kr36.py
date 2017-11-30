# coding=utf8
from website.common.site import WebSite
from website.kr36.kr36Commments import Kr36Comments

class Kr36(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ThirtysixKrypton'
        self.pattern = r'^http[s]{0,1}://36kr\.com\.*'
        self.setcommentimpl(Kr36Comments())