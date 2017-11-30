# coding=utf8
from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.common.bbss2postquery import BBSS2PostQuery 

class OneThreeOne(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '131'
        self.pattern = r'http[s]{0,1}://.*\.131(qz)?\.com.*'
        #self.setcommentimpl(CommenComments())
        #self.sets2queryimpl(BBSS2PostQuery('http://bbs.131.com/search.php?mod=forum'))
        return