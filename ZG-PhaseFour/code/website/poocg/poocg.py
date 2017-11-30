# coding=utf8
from website.common.site import WebSite
from website.poocg.poocgNewsComments import poocgNewsComments

class poocg(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'poocg'
        self.pattern = r'^http[s]{0,1}://www\.poocg\.com/.*'
        self.setcommentimpl(poocgNewsComments())
        return