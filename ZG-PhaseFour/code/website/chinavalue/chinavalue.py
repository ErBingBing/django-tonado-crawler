# coding=utf8
from website.common.site import WebSite
from website.chinavalue.chinavaluecomments import Chinavaluecomments

class Chinavalue(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'chinavalue'
        self.pattern = r'^http[s]{0,1}://www\.chinavalue\.net\.*'
        self.setcommentimpl(Chinavaluecomments())