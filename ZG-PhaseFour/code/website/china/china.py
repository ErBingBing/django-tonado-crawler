# coding=utf8

from website.common.site import WebSite
from website.china.chinacomments import ChinaComments


class China(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'china'
        self.pattern = r'^http[s]{0,1}://\w+\.china\.com.*'
        self.setcommentimpl(ChinaComments())
            