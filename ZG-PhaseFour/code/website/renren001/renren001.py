# encoding=utf8
from website.common.site import WebSite
from website.renren001.renren001comments import Renren001Comments
from  website.renren001.renrenquery import S2Query
from utility.regexutil import RegexUtility

class Renren001(WebSite):
    def __init__(self):
        WebSite.__init__(self)  
        self.name = 'hqcx'
        self.patterns = [r'^http://www\.renren001\.cc/\w+/\w+/player\.html',r'^http://www\.renren001\.cc/\w+/\w+.*']
        self.setcommentimpl(Renren001Comments())
        self.sets2queryimpl(S2Query())
        return
    
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False   