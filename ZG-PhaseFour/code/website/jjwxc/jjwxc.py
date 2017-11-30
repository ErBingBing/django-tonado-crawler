# coding=utf8

from website.common.site import WebSite
from website.jjwxc.jjwxccomments import JjwxcComments


class Jjwxc(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'jjwxc'
        self.pattern = r'^http[s]{0,1}://.*\.jjwxc\.net/.*'
        self.setcommentimpl(JjwxcComments())
        

