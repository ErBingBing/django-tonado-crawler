# coding=utf8
from website.common.site import WebSite
from website.toutiao.toutiaonewscomments import ToutiaoNewsComments

class Toutiao(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'Toutiao'
        self.pattern = r'^http[s]{0,1}://www\.toutiao\.com\.*'
        self.setcommentimpl(ToutiaoNewsComments())