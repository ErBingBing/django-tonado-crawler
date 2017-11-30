# coding=utf8
from website.common.site import WebSite
from website.common.basicinfo import SiteBasicInfo
from website.fun.funcomments import FunComments
import re

from website.fun.funquery import FunS2Query


class Fun(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'fun'
        self.pattern = r'^http[s]{0,1}://.*\.fun\.tv/.*'
        self.setcommentimpl(FunComments())
        self.sets2queryimpl(FunS2Query())
