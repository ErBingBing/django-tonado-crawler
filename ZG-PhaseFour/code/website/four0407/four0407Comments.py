# encoding=utf-8
##############################################################################################
# @file：Four0407Comments.py
# @author：yongjicao
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：40407新闻页获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/17
# @note:第53行正则表达式匹配异常没做处理
###############################################################################################

from website.common.comments import SiteComments
from website.common.changyanComments import changyanComments
from log.spiderlog import Logger
import re

##############################################################################################
# @class：Four0407Comments
# @author：yongjicao
# @date：2016/12/12
# @note：40407新闻页获取评论的类，继承于SiteComments类
##############################################################################################
class Four0407Comments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：yongjicao
    # @date：2016/12/12
    # @note：40407新闻页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.changyan = None

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：yongjicao
    # @date：2016/12/12
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        #topicSourceId = re.findall(r'^http://\w+\.40407\.com/\w+/\d+/(\d+).*', proparam.originalurl).__getitem__(0)
        topicSourceId = re.findall(r'^http://\w+\.40407\.com/\w+/\d+/(\d+).*', proparam.originalurl)
        if topicSourceId:
            topicSourceId = topicSourceId[0]
        else:
            Logger.getlogging().warning('{0} Can\'t find the topicSourceId'.format(proparam.originalurl))
            Logger.getlogging().warning('{0}:30000'.format(proparam.originalurl))
            return 
        self.createobject().getcomments(proparam, topicSourceId, 3, 2)

    def createobject(self):
        if self.changyan is None:
            self.changyan = changyanComments(self)
        return self.changyan



