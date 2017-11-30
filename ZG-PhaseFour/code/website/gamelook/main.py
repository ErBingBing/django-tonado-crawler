# encoding=utf8
from website.common.site import WebSite
#from website.gamelook.AllComments import AllComments

class gamelook(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gamelook'
        self.patterns = [r'^http://www\.gamelook\.com.cn/\d{4}/\d{2}/\d+']
        #self.setcommentimpl(AllComments())