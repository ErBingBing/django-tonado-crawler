# encoding=utf8
from website.common.site import WebSite
#from website.sootoo.ALLComments import AllComments
from website.common.changyanComments import ChangyanComments

class Sootoo(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'sootoo'
        self.pattern = '^http://www\.sootoo\.com/.*'
        self.setcommentimpl(ChangyanComments())
