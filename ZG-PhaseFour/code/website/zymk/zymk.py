# coding=utf8
from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.common.bbss2postquery import BBSS2PostQuery 

class Zymk(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'zymk'
        self.pattern = r'^http://.*\.zymk\.cn\/.*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.zymk.cn/search.php?mod=forum'))
