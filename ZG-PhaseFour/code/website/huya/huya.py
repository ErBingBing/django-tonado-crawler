# coding=utf8

from website.common.site import WebSite
from website.huya.huyacomments import HuyaComments
from website.huya.huyaquery import HuyaS2Query

class Huya(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'huya'
        self.pattern = r'^http[s]{0,1}://.*\.huya\.com/.*'
        self.setcommentimpl(HuyaComments())
        self.sets2queryimpl(HuyaS2Query())
        return