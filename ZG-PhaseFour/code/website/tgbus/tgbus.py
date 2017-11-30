# coding=utf8
from website.common.site import WebSite
from utility.bbs2commom import CommenComments
from website.tgbus.tgbusquery import TGbusS2Query


class TgBus(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tgbus'
        #self.pattern = r'^http://bbs\.zol\.com\.cn/[a-z]*/\w+(_\d+)*\.html'
        self.pattern = r'http[s]{0,1}://.*\.tgbus\.com.*'
        self.setcommentimpl(CommenComments())
        self.sets2queryimpl(TGbusS2Query())
