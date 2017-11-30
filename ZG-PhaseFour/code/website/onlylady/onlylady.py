# coding=utf8
from website.common.site import WebSite
from website.onlylady.onlyladyComments import OnlyladyComments



class Onlylady(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'onlylady'
        self.pattern = r'^http[s]{0,1}://.*\.onlylady\.com\/*'
        self.setcommentimpl(OnlyladyComments())