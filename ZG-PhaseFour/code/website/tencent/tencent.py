# coding=utf8

from website.common.site import WebSite
from website.tencent.tencentcomments import TencentComments
from website.tencent.tencentquery import TencentS2Query
from website.common.bbss2postquery import BBSS2PostQuery 

class Tencent(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tencent'
        self.patterns = [r'^http[s]{0,1}://.*\.qq\.com/.*',
                         r'^http[s]{0,1}://p\.weather\.com\.cn',
                         r'^http[s]{0,1}://news\.sogou\.com.*']        
        self.setcommentimpl(TencentComments())
        self.sets2queryimpl(TencentS2Query())
        #self.sets2queryimpl(BBSS2PostQuery('http://bbs.book.qq.com/search.php?mod=forum'))
       

        


