# coding=utf8
from website.common.site import WebSite
from website.duowan.duowancomments import DuowanComments
from website.duowan.duowanquery import DuowanQuery

from website.common.bbss2postquery import BBSS2PostQuery 
class Duowan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'duowan'
        self.pattern = '^http://\w+\.duowan\.com/*'
        self.setcommentimpl(DuowanComments())
        self.sets2queryimpl(DuowanQuery())
        #self.setcommentimpl(CommenComments())
        #self.sets2queryimpl(BBSS2PostQuery('http://bbs.duowan.com/search.php?mod=forum'))
        return