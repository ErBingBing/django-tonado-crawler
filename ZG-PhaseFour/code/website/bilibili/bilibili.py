# coding=utf-8
##############################################################################################
# @file：bilibili.py
# @author：Han Luyang
# @date：2017/09/11
# @note：bilibili网站配置文件
##############################################################################################

from website.common.site import WebSite
from website.bilibili.bilibiliComments import BilibiliComments
from website.bilibili.bilibiliquery import BilibiliS2Query


class Bilibili(WebSite):
    def __init__(self):
        WebSite.__init__(self)
        self.name = 'bilibili'
        self.pattern = '^https?://www\.bilibili\.com/.*'
        self.setcommentimpl(BilibiliComments())
        self.sets2queryimpl(BilibiliS2Query())
