# encoding=utf-8

##############################################################################################
# @file：sfacgcomment.py
# @author：Hedian
# @date：2016/12/29
# @version：Ver0.0.0.100
# @note：SF互动传媒网获取评论的文件
##############################################################r################################

from website.common.comments import SiteComments
from log.spiderlog import Logger
from website.sfacg.bookcomments import BookComments
from website.sfacg.newscomments import NewsComments


##############################################################################################
# @class：SfacgComments
# @author：Hedian
# @date：2016/12/29
# @note：SF互动传媒网获取评论的类，继承于SiteComments类
##############################################################################################
class SfacgComments(SiteComments):
    STEP_1 = None

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/12/29
    # @note：SfacgComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.news = None
        self.book = None

    def createobject(self):
        if self.news is None:
            self.news = NewsComments(self)
        if self.book is None:
            self.book = BookComments(self)



    ##############################################################################################
    # @functions：process
    # @params：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：none
    # @author：Hedian
    # @date：2016/12/29
    # @note：根据原始url得到子域名，根据不同的子域名调用不同的类处理
    ##############################################################################################
    def process(self, params):

        self.createobject()
        try:
            # Step1: 通过url得到子域名
            field = self.r.parse('^http[s]{0,1}://(\w+)\.?', params.originalurl)[0]
            params.customized['field'] = field
            if field in ['news', 'comic']:
                # SF互动传媒网新闻,部分漫画处理
                self.news.process(params)
            elif field in ['manhua', 'book']:
                # SF互动传媒网轻小说,部分漫画处理
                self.book.process(params)
            else:
                # SF互动传媒网其他处理
                pass

        except:
            Logger.printexception()