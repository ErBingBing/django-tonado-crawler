# encoding=utf8
from website.common.site import WebSite
from website.ithome.AllComments import AllComments

class ithome(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ithome'
        self.pattern = r'^http[s]{0,1}://www\.ithome\.com/.*'
        self.setcommentimpl(AllComments())