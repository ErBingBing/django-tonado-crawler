# coding=utf8
from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments

class Game3dm(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.pattern = r'^http://\w+\.3dmgame\.com.*'
        self.setcommentimpl(ChangyanComments())