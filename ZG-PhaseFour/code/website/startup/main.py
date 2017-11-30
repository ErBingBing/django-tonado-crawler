# encoding=utf8
from website.common.site import WebSite
from website.startup.AllComments import AllComments
from utility.regexutil import RegexUtility

class startup(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'startup'
        self.patterns = [r'^http://news\.startup\-partner\.com/news/\d+.html']
        self.setcommentimpl(AllComments())
        
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False