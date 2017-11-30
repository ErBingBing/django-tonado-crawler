# coding=utf8
from website.common.site import WebSite
from website.rayli.rayliComments import rayliComments
from utility.bbs2commom import CommenComments

class rayli(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://bbs\.rayli\.com\.cn/.*'
        self.setcommentimpl(rayliComments())
        # self.setcommentimpl(CommenComments())
        return