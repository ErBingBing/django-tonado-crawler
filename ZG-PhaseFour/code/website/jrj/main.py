# encoding=utf8
from website.common.site import WebSite
from website.jrj.AllComments import AllComments
from utility.regexutil import RegexUtility

class jrj(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'jrj'
        self.patterns = [r'^http://\w+\.jrj\.com\.cn/\d+/\d+/\d+\.shtml',r'^http://\w+\.jrj\.com\.cn/\w+/\d+/\d+/\d+\.shtml']
        self.setcommentimpl(AllComments())
        
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False    