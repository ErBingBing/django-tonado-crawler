# coding=utf8
from website.common.site import WebSite
from website.joyme.joymecomments import JoyComments



class Joyme(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'joyme'
        self.pattern = r'^http[s]{0,1}://www\.joyme\.com\/news\/*'
        self.setcommentimpl(JoyComments())