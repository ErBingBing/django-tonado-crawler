# coding=utf8
from website.common.site import WebSite
from website.tmtpost.tmtpostcommnets import Tmtpostcommnets

class Tmtpost(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'tmtpost'
        self.pattern = r'^http[s]{0,1}://.*\.tmtpost\.com\.*'
        self.setcommentimpl(Tmtpostcommnets())