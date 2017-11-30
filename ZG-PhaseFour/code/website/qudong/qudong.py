
# coding=utf8

from website.common.site import WebSite
from website.common.changyanComments import ChangyanComments



class Qudong(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'qudong'
        self.pattern = r'^http[s]{0,1}://.*\.qudong\.com'
        self.setcommentimpl(ChangyanComments())
        













