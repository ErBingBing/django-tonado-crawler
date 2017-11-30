# coding=utf8
from website.common.site import WebSite
from website.mop.mopComments import MopComments
from website.mop.mopquery import MopS2Query
class Mop(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.addpattern(r'^http://.*mop\.com/.*')
        #self.addpattern('http?://zhannei\.baidu\.com/cse/search')
        # self.sets1basicimpl(MopS1Basic())
        self.setcommentimpl(MopComments())
        self.sets2queryimpl(MopS2Query())
        # self.sets3extractimpl(MopS3Extract())