# encoding=utf-8

##############################################################################################
# @file：.py
# @author：Hedian
# @date：2016/12/15
# @version：Ver0.0.0.100
# @note：机锋网获取评论的文件
##############################################################r################################

from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.bbs2commom import CommenComments
from website.common.changyanComments import ChangyanComments

##############################################################################################
# @class：GfanComments
# @author：Hedian
# @date：2016/12/15
# @note：机锋网获取评论的类，继承于SiteComments类
##############################################################################################
class GfanComments(SiteComments):
    STEP_1 = None

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/12/15
    # @note：GfanComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.bbs = None
        self.news = None

    def createobject(self):
        if self.bbs is None:
            self.bbs = CommenComments(self)
        if self.news is None:
            self.news = ChangyanComments(self)

    ##############################################################################################
    # @functions：process
    # @params：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：
    # @author：Hedian
    # @date：2016/12/15
    # @note：
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.originalurl)
        self.createobject()

        field = self.r.parse('^http://(\w+)\.?', params.originalurl)[0]
        Logger.getlogging().debug(field)

        if field == 'bbs':
            # 机锋网论坛
            self.bbs.process(params)
        else:
            # 机锋网其他处理
            self.news.process(params)


