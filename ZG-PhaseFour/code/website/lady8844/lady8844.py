# coding=utf8
from website.common.site import WebSite
#from website.lady8844.lady8844Comments import Lady8844Comments
from utility.bbs2commom import CommenComments 



class Lady8844(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'lady8844'
        self.pattern = r'^http[s]{0,1}://.*lady8844\.com.*'
        self.setcommentimpl(CommenComments())
        