# coding=utf8

from website.common.site import WebSite
from website.angeeks.angeeksquery import AngeeksS2Query
from utility.bbs2commom import CommenComments 
class Angeeks(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'Angeeks'
        self.pattern = r'^http[s]{0,1}://.*\.angeeks\.com/.*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(AngeeksS2Query())