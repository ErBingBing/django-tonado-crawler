# encoding=utf8
from website.common.site import WebSite
from website.pcgames.pcgamescomments import PcgamesComments
from website.pcgames.pcgamesquery import S2Query

class Pcgames(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'pcgames'
        self.pattern = r'^http[s]{0,1}://.*\.pcgames\.com\.cn/.*'
        self.setcommentimpl(PcgamesComments())
        self.sets2queryimpl(S2Query())
        return