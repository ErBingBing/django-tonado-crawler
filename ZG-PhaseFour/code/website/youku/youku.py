# coding=utf8
from website.common.site import WebSite
from website.youku.youkucomments import YoukuComments
from website.youku.youkuquery import YoukuS2Query
from website.common.basicinfo import SiteBasicInfo
import re

class Youku(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'youku'
        self.pattern = '^http[s]{0,1}://.*\.youku\.com/.*|^http://v\.laifeng\.com/.*'
        self.setcommentimpl(YoukuComments())
        self.sets2queryimpl(YoukuS2Query())
        return