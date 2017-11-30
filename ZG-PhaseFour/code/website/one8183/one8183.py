# coding=utf8
from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.one8183.one8183comments import One8183Comments
from website.common.bbss2postquery import BBSS2PostQuery 


class One8183(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '18183'
        self.pattern = r'http[s]{0,1}://.*\.18183\.com.*'
        self.setcommentimpl(One8183Comments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.18183.com/search.php?mod=forum'))
        return