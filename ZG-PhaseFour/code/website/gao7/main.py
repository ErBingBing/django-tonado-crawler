# coding=utf8

from website.common.site import WebSite
from website.common.bbss2postquery import BBSS2PostQuery 
from utility.bbs2commom import CommenComments
class gao7(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gao7'
        self.pattern = r'^http[s]{0,1}://.*\.gao7\.com/.*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.gao7.com/search.php?mod=forum'))
        return