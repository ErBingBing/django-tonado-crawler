# coding=utf8
from website.common.site import WebSite
from website.dm5.dm5Commnets import Dm5Commnets

class Dm5(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'dm5'
        self.pattern = r'^http[s]{0,1}://.*\.dm5\.com/*'
        self.setcommentimpl(Dm5Commnets())