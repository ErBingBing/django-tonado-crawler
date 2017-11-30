# coding=utf8
from website.common.site import WebSite
from website.kankan.kankancomments import KanKanComments
from website.kankan.kankanquery import KanKanS2Query

class KanKan(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'kankan'
        #self.patterns = [r'^http://\w+\.kankan\.com/',
                         #r'^http://\w+\.kankan\.com/(\w+/)?\w+/\d+/\d+\.shtml/.*']
        self.pattern = r'^http://.*\.kankan\.com/.*'
        self.setcommentimpl(KanKanComments())
        self.sets2queryimpl(KanKanS2Query())
        return