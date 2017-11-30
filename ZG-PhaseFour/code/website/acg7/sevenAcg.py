# coding=utf8
from website.common.site import WebSite
from website.common.bbss2postquery import BBSS2PostQuery 
from utility.bbs2commom import CommenComments

class SevenAcg(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'acg7'
        self.pattern = r'^http://www\.7acg\.com\/*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(BBSS2PostQuery('http://www.7acg.com/search.php?mod=forum'))
    