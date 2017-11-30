# coding=utf8
from website.common.site import WebSite
from website.gameres.gameresnewscomments import GameresNewsComments

class Gameres(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'Gameres'
        self.pattern = r'^http[s]{0,1}://www\.gameres\.com\.*'
        self.setcommentimpl(GameresNewsComments())