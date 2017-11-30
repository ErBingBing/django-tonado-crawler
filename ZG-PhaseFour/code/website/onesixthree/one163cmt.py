# encoding=utf-8

from website.common.comments import SiteComments
from website.onesixthree.onesixthreecomments import Comments163
from website.onesixthree.yueducomments import YueduComments
from website.onesixthree.vcomments import VComments



class One63Comments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：none
    ################################################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.onesixthreeNews = None
        self.onesixthreeYuedu = None
        self.onesixthreeV = None

    def createobject(self):
        if self.onesixthreeNews is None:
            self.onesixthreeNews = Comments163()
        if self.onesixthreeYuedu is None:
            self.onesixthreeYuedu = YueduComments(self)
        if self.onesixthreeV is None:
            self.onesixthreeV = VComments(self)

    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：none
    ################################################################################################################
    def process(self, params):
        # 初始化内部子类对象
        self.createobject()

        # 阅读评论取得
        if self.r.match('http://(\w+.)?yuedu\.163\.com/.*', params.originalurl):
            self.onesixthreeYuedu.process(params)
        # 新闻评论取得
        elif self.r.match('http://.+\.163\.com/.*', params.originalurl):
            self.onesixthreeNews.process(params)
        # 视频评论取得
        #网易视频改版为直播,不在作业范围内
        # elif self.r.match('http://v\.163\.com/.*', params.originalurl):
        #     self.onesixthreeV.process(params)