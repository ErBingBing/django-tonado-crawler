# encoding=utf8
from website.common.site import WebSite
from website.jianshu.AllComments import AllComments
from utility.regexutil import RegexUtility

class jianshu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'jianshu'
        self.patterns = [r'^http://www\.jianshu\.com/p/\w+']
        # self.setcommentimpl(AllComments())
        
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False            