# coding=utf8
from website.common.site import WebSite
from website.book2200.bookComments import bookComments

class book(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '2200book'
        self.pattern = r'^http://www\.2200book\.com/.*'
        self.setcommentimpl(bookComments())
        return