# encoding=utf8
from website.common.site import WebSite
from website.qidian.qidiancomments import QidianComments
from utility.regexutil import RegexUtility

class qidian(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'qidian'
        self.patterns = [r'^http://www\.qidian\.com/Book/\d+\.aspx',r'^http://book\.qidian\.com/info/\d+',r'^http://www\.qdmm\.com/MMWeb/\d+.aspx',r'^http://www.yuncheng.com/list/\w+']
        self.setcommentimpl(QidianComments())
        
    def match(self, url):
        for pt in self.patterns:
            if RegexUtility.match(pt, url):
                return True
        return False