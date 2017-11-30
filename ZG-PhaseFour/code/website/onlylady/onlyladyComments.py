# encoding=utf8

##############################################################################################
# @file：onlyladyComments.py
# @author：Yangming
# @date：2016/12/10
# @version：Ver0.0.0.100
# @note：女人志获取评论的文件
##############################################################################################

import traceback

from log.spiderlog import Logger
from website.common.comments import SiteComments
from website.onlylady.onlyladyBbsComments import OnlyladyBbsComments
from utility.bbs2commom import CommenComments


##############################################################################################
# @class：onlyladyComments
# @author：Yangming
# @date：2016/12/10
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class OnlyladyComments(SiteComments):
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yangming
    # @date：2016/12/10
    # @note：构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteComments.__init__(self)
        self.onlyladyBbs = None

    ################################################################################################################
    # @functions：createobject
    # @params： see WebSite.createobject
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def createobject(self):
        if self.onlyladyBbs is None:
            self.onlyladyBbs = OnlyladyBbsComments(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    # @author：Yangming
    # @date：2016/12/10
    # @note：Step1：通过共通模块传入的html内容获取到key,生成当前页数和总页数，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            # 初始化内部子类对象
            self.createobject()
            # 论坛评论取得
            if self.r.match('http://bbs.onlylady.com/.*', params.originalurl):
                # self.onlyladyBbs.process(params)
                # bbs获取评论调用共通方法,onlyladyBdsComments已测试通过
                CommenComments(self).process(params)
        except Exception, e:
            traceback.print_exc()
