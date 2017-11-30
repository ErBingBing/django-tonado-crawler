# coding=utf8

from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.common.bbss2postquery import BBSS2PostQuery 


class Gxdmw(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        self.name = 'gxdmw'
        self.pattern = r'^http[s]{0,1}://www\.gxdmw\.com/.*'
        self.setcommentimpl(CommenComments())
        #self.sets2queryimpl(BBSS2PostQuery('http://www.gxdmw.com/search.php?mod=portal'))

        