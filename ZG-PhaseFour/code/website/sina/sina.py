# coding=utf8
################################################################################################################
# @file: sina.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
from website.common.site import WebSite
from website.sina.sinacomments import SinaComments
from website.sina.sinaquery import SinaS2Query


################################################################################################################
# @class：SIna
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Sina(WebSite):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        WebSite.__init__(self)
        # 处理URL模板
        self.addpattern(r'^http[s]{0,1}://.*sina\.com\.cn.*')
        # 设置评论获取实例
        self.setcommentimpl(SinaComments())
        # 设置S2搜索实例
        self.sets2queryimpl(SinaS2Query())

