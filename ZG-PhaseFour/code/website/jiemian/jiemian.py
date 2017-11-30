# coding=utf8
from website.common.site import WebSite
from website.jiemian.jiemianComments import jiemianComments

class jiemian(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://www\.jiemian\.com/.*'
        self.setcommentimpl(jiemianComments())
        return