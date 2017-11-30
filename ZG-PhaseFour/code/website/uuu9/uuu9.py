# coding=utf8

from website.common.site import WebSite
from website.uuu9.uuu9comments import Uuu9Comments

class Uuu9(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'uuu9'
        self.pattern = r'^http[s]{0,1}://.*\.uuu9\.com/.*'
        self.setcommentimpl(Uuu9Comments())
        #self.sets2queryimpl(DmzjS2Query())
        return