# encoding=utf8
from website.common.site import WebSite
from website.dm78.dm78comments import dm78Comments
#from website.dm78.dm78dmquery import S2Query
from website.common.bbss2postquery import BBSS2PostQuery 

class Dm78(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '78dm'
        self.pattern = r'^http://.*\.78dm\.net/.*'
        self.setcommentimpl(dm78Comments())
        #self.sets2queryimpl(S2Query())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.78dm.net/search.php?mod=forum'))