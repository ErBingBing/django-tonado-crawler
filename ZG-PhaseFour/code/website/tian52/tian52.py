# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments
from website.tian52.tian52query import tian52S2Query

class tian52(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://www\.52tian\.net/.*'
        self.setcommentimpl(ChangyanComments())
        self.sets2queryimpl(tian52S2Query())