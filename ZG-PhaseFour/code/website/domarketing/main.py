# encoding=utf8
from website.common.site import WebSite
from website.domarketing.AllComments import AllComments
from utility.regexutil import RegexUtility

class domarketing(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'domarketing'
        self.pattern = r'^http://www\.domarketing\.org/.*'
        self.setcommentimpl(AllComments())
        
