# coding=utf8
from website.common.site import WebSite
from website.gamersky.gamerskycomments import GamerSkyComments
from website.common.bbss2postquery import BBSS2PostQuery 

class Gamersky(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gamersky'
        self.pattern = r'^http://\w+\.gamersky\.com/.*'
        self.setcommentimpl(GamerSkyComments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.gamersky.com/search.php?mod=forum'))
        return