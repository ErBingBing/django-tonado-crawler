# coding=utf8
from website.common.site import WebSite
from website.ishangman.ishangmanComments import ishangmanComments

class ishangman(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ishangman'
        self.pattern = r'^http://\w+\.ishangman\.com/.*'
        self.setcommentimpl(ishangmanComments())
        return