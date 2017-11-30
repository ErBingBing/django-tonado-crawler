# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import changyanComments
class Four0407(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = '40407'
        self.pattern = r'^http://\w+\.40407\.com.*'
        #self.setcommentimpl(changyanComments())