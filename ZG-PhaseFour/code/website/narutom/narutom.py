# coding=utf8

from website.common.site import WebSite
#from website.narutom.narutomcomments import NarutomComments
from website.narutom.narutomquery import NarutomS2Query
from utility.bbs2commom import CommenComments

class Narutom(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'narutom'
        self.pattern = r'^http[s]{0,1}://.*\.narutom\.com/.*'
        #self.setcommentimpl(CommenComments())
        self.sets2queryimpl(NarutomS2Query())
        return