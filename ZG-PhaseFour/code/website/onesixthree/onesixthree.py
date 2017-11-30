# coding=utf8
from website.common.site import WebSite
from website.onesixthree.one63query import One63S2Query
from website.onesixthree.one163cmt import One63Comments



class OneSixThree(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '163'
        self.addpattern(r'^http[s]{0,1}://.*\.163\.com.*')
        self.setcommentimpl(One63Comments())
        self.sets2queryimpl(One63S2Query())
    


