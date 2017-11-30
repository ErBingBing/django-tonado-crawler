# coding=utf8

from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.common.bbss2postquery import BBSS2PostQuery 

class Gametanzi(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gametanzi'
        self.pattern = r'^http[s]{0,1}://.*\.gametanzi\.com/.*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.gametanzi.com/search.php?mod=forum'))
        return