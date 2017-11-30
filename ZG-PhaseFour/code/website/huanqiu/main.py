# encoding=utf8
from website.common.site import WebSite
from website.huanqiu.AllComments import AllComments
from utility.regexutil import RegexUtility

class huanqiu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'huanqiu'
        self.patterns = [r'^http://tech\.huanqiu\.com/diginews/.*']
        self.setcommentimpl(AllComments())
        
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False