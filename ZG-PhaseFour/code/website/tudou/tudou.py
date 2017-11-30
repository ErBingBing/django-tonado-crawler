# encoding=utf8
from website.common.site import WebSite
from website.tudou.tudoucomments import TudouComments
from website.tudou.tudouquery import tudouS2Query

class Tudou(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tudou'
        self.pattern = '^http[s]{0,1}://(www|video)\.tudou\.com/.*'
        self.setcommentimpl(TudouComments())
        self.sets2queryimpl(tudouS2Query())
        return
