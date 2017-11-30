# coding=utf8
from website.common.site import WebSite
from website.thirtysixKrypton.thirtysixKryptonCommments import ThirtysixKryptonComments

class ThirtysixKrypton(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ThirtysixKrypton'
        self.pattern = r'^http[s]{0,1}://36kr\.com\.*'
        self.setcommentimpl(ThirtysixKryptonComments())