# coding=utf-8

from website.common.site import WebSite
from website.syqnr.syqnrcomments import SyqnrComments
#from website.syqnr.syqnrbasicinfo import SyqnrBasicInfo


class Syqnr(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'syqnr'
        self.pattern = r'^http[s]{0,1}://.*\.syqnr\.com/.*'
        self.setcommentimpl(SyqnrComments())
        #self.basicinfo = SyqnrBasicInfo()
        

