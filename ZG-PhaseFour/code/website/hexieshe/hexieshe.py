# coding=utf8
from website.common.site import WebSite
from website.hexieshe.hexiesheComments import HexiesheComments



class Hexieshe(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'hexieshe'
        self.pattern = r'^http[s]{0,1}://.*\.hexieshe\.com\/*\/'
        self.setcommentimpl(HexiesheComments())