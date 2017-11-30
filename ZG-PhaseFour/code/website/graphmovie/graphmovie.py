# coding=utf8
from website.common.site import WebSite
from website.graphmovie.graphmoviepostcomments import GraphmoviePostComments 


class Graphmovie(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'graphmovie'
        self.pattern = r'^^http://\w+\.graphmovie[s]{0,1}\.com.*'
        self.setcommentimpl(GraphmoviePostComments())