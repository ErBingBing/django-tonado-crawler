# coding=utf8
from website.common.site import WebSite
from website.ea3w.ea3wcomments import Ea3wcomments



class Ea3w(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ea3w'
        self.pattern = r'^http[s]{0,1}://\w+\.ea3w\.com\/*'
        self.setcommentimpl(Ea3wcomments())