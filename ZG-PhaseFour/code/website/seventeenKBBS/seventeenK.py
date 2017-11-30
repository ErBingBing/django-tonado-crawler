# coding=utf8
from website.common.site import WebSite
from website.seventeenKBBS.seventeenKComments import SeventeenKComments



class SeventeenK(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'seventeenKBBS'
        self.pattern = r'^http://bbs\.17k\.com\/*'
        self.setcommentimpl(SeventeenKComments())