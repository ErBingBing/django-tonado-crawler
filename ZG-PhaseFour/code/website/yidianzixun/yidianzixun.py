# coding=utf8

from website.common.site import WebSite
from website.yidianzixun.yidianzixuncomments import YidianzixunComments


class Yidianzixun(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tencent'
        self.pattern = r'^http[s]{0,1}://.*\.yidianzixun\.com/.*'
        self.setcommentimpl(YidianzixunComments())
        #self.basicinfo = YidianzixunBasicInfo()
        


