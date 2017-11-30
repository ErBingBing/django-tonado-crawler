# coding=utf8
from website.common.site import WebSite
from website.pcauto.PcautoComments import PcautoComments
import re

class Pcauto(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'pcauto'
        self.pattern = '^http://www\.pcauto\.com.cn.*'
        self.setcommentimpl(PcautoComments())
