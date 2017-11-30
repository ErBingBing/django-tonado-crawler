# coding=utf8
from website.common.site import WebSite
from website.dmzj.dmzjcomments import DmzjComments
#from website.dmzj.dmzjquery import DmzjS2Query
#from website.common.bbss2postquery import BBSS2PostQuery 
from website.dmzj.dmzjquery import DmzjQuery

class Dmzj(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'dmzj'
        self.pattern = r'^http[s]{0,1}://.*\.dmzj\.com/.*'
        self.setcommentimpl(DmzjComments())
        self.sets2queryimpl(DmzjQuery())
        #self.sets2queryimpl(BBSS2PostQuery('http://bbs.dmzj.com/search.php?mod=forum'))
        #self.sets2queryimpl(DmzjS2Query())