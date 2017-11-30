# coding=utf8
from website.common.site import WebSite
from website.baidu.baiduquery import BaiduS2Query
from website.baidu.baidutiebacomments import BaiduTiebaComments 

class Baidu(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'baidu'
        self.pattern = r'^http[s]{0,1}://.*\.baidu\.com.*'
        self.setcommentimpl(BaiduTiebaComments())
        self.sets2queryimpl(BaiduS2Query())