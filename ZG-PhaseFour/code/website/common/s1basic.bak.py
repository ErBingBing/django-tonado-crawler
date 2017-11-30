# coding=utf-8

################################################################################################################
# @file: site.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
# @modify
# @author:Jiangsiwei
################################################################################################################
from configuration import constant
from dao.mongodao import MongoDAO
from storage.newsstorage import NewsStorage
from utility.regexutil import RegexUtility

################################################################################################################
# @class：SiteBasicInfo
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from storage.urlmanager import URLManager, URLContext
from utility.xpathutil import XPathUtility


class SiteS1Basic:

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SiteBasicInfo初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.website = None
        self.r = RegexUtility()
    ################################################################################################################
    # @functions：process
    # @param： none
    # @return：none
    # @note：获取网页基本信息
    ################################################################################################################
    def process(self, params):
        title = params.page_title
        if not title:
            title = XPathUtility(params.content).gettitle('/html/head/title')
        # 设置URL的标题、正文、发布时间信息
        dict = { MongoDAO.SPIDER_COLLECTION_NEWS_TITLE:title,
                 MongoDAO.SPIDER_COLLECTION_NEWS_BODY: params.page_body,
                 MongoDAO.SPIDER_COLLECTION_NEWS_PUBLISH_DATE: params.html_time}
        NewsStorage.seturlinfos(params.url, dict)

    ################################################################################################################
    # @functions：setwebsite
    # @website： 主站
    # @return：none
    # @note：设置主站
    ################################################################################################################
    def setwebsite(self, website):
        self.website = website

    ################################################################################################################
    # @functions：保存首页图片URL
    # @url： 图片url
    # @originalurl： 新闻页URL
    # @return：none
    # @note：下载新闻页图片
    ################################################################################################################
    def storeurl(self, url, originalurl, step, others={}):
        urlparam = URLContext()
        urlparam.url = url
        urlparam.originalurl = originalurl
        urlparam.step = step
        urlparam.type = URLContext.S1_MAIN_BODY
        urlparam.customized = others
        URLManager.getinstance().storeurl(url, urlparam, constant.REQUEST_TYPE_IMG)
