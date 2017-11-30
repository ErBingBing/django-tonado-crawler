# encoding=utf-8
##############################################################################################
# @file：SfwComments.py
# @author：yongjicao
# @date：2016/12/06
# @version：Ver0.0.0.100
# @note：上方网获取评论的文件
###############################################################################################

from website.common.comments import SiteComments
#from website.common.changyanNewsComments import changyanNewsComments
from website.common.changyanComments import changyanComments
from log.spiderlog import Logger
import re

##############################################################################################
# @class：SfwComments
# @author：yongjicao
# @date：2016/12/06
# @note：上方网获取评论的类，继承于SiteComments类
##############################################################################################
class SfwComments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：yongjicao
    # @date：2016/12/06
    # @note：上方网类的构造器，初始化内部变量
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
    # @date：2016/12/06
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        topicSourceId = re.findall(r'^http://\w+\.sfw\.cn/\w+/(\d+).html', proparam.originalurl).__getitem__(0)
        self.createobject().getcomments(proparam, topicSourceId, 3, 2)

    def createobject(self):
        if self.changyan is None:
             self.changyan = changyanComments(self)
        return self.changyan



