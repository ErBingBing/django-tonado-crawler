# coding=utf8

from website.common.site import WebSite
from website.tianya.tianyacomments import TianyaComments
from website.tianya.tianyaquery import TianyaS2Query

class Tianya(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tianya'
        self.pattern = r'^http[s]{0,1}://.*\.tianya\.cn/.*'
        self.setcommentimpl(TianyaComments())
        self.sets2queryimpl(TianyaS2Query())        
        

