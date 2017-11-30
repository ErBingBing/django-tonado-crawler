# coding=utf-8

##############################################################################################
# @file：uuu9comments.py
# @author：Hedian
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：游久网站获取评论的文件
##############################################################r################################

from website.common.comments import SiteComments
from log.spiderlog import Logger
from website.uuu9.newscomments import NewsComments
from utility.bbs2commom import CommenComments

##############################################################################################
# @class：Uuu9Comments
# @author：Hedian
# @date：2016/11/30
# @note：游久网站获取评论的类，继承于SiteComments类
##############################################################################################
class Uuu9Comments(SiteComments):
    BBS_URL_REG = '^http://moba\.uuu9\.com/\w+-\d+-(\d+)-\d+.html'
    PAGE_SIZE = 10
    BBS_TITLE = ''
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/30
    # @note：Uuu9Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.bbs = None
        self.news = None

    def createobject(self):
        if self.bbs is None:
            self.bbs = CommenComments(self)
        if self.news is None:
            self.news = NewsComments(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/30
    # @note：AppgameComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):

        field = self.r.parse('^http://(\w+)\.?', params.url)[0]
        params.customized['field'] = field
        Logger.getlogging().debug(field)

        self.createobject()

        field = self.r.parse('^http://(\w+)\.uuu9\.com*', params.originalurl)[0]
        # 论坛
        if field == 'moba':
            self.bbs.process(params)
        else:
            self.news.process(params)
