# coding=utf8

from website.common.site import WebSite
from website.iqiyi.iqiyicomments import IqiyiComments
from website.iqiyi.iqiyiquery import IqiyiS2Query

class Iqiyi(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'iqiyi'
        self.pattern = r'^http[s]{0,1}://.*\.iqiyi\.com/.*'
        self.setcommentimpl(IqiyiComments())
        self.sets2queryimpl(IqiyiS2Query())
        return