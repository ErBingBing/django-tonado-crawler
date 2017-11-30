# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments
from website.kumi.kumiquery import kumiS2Query

class kumi(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'kumi'
        self.pattern = r'^http://.*\.kumi\.cn/.*'
        self.setcommentimpl(ChangyanComments())
        self.sets2queryimpl(kumiS2Query())