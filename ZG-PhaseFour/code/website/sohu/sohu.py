# coding=utf8

from website.common.site import WebSite
from website.sohu.sohucomments import SohuComments
from website.sohu.sohuquery import SohuS2Query
#from website.sohu.sohuextract import SohuS3Extract
#from website.sohu.sohubasic import SohuS1Basic


class Sohu(WebSite):

    def __init__(self):
        WebSite.__init__(self)
        # 处理URL模板
        self.addpattern(r'^http[s]{0,1}://.*\.sohu\.com.*')
        # 设置S3头条抽取实例
        #self.sets3extractimpl(SohuS3Extract())
        # 设置基本信息获取实例
        #self.sets1basicimpl(SohuS1Basic())
        self.setcommentimpl(SohuComments())
        self.sets2queryimpl(SohuS2Query())




