# coding=utf8
from website.common.site import WebSite
from website.ifeng.ifengquery import IfengS2Query
from website.ifeng.ifengnews import IfengNewsComments 


class Ifeng(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'ifeng'
        self.pattern = r'^http[s]{0,1}://.*ifeng\.com\/.*'
        self.setcommentimpl(IfengNewsComments())
        self.sets2queryimpl(IfengS2Query())
        return