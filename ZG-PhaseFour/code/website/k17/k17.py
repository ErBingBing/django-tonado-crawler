# coding=utf8
from website.common.site import WebSite
from website.k17.k17comments import Comments
from website.common.basicinfo import SiteBasicInfo
from website.common.bbss2postquery import BBSS2PostQuery 

class K17(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'k17'
        self.pattern = r'^http://\w+\.17k\.com.*'
        self.setcommentimpl(Comments())
        self.sets2queryimpl(BBSS2PostQuery('http://bbs.17k.com/search.php?mod=forum'))