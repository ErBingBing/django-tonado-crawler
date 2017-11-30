# encoding=utf8
from website.common.site import WebSite
from website.chinabyte.chinabytecomments import ChinabyteComments
from utility.regexutil import RegexUtility

class Chinabyte(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'chinabyte'
        self.patterns = [r'^http://\w+\.chinabyte\.com/.*']
        self.setcommentimpl(ChinabyteComments())
