# coding=utf-8
#
################################################################################################################
# @file: site.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
# @modify
################################################################################################################
import re
import time
#
from configuration import constant
from configuration.constant import SPIDER_CHANNEL_S2, SPIDER_S2_WEBSITE_TYPE
from configuration.environment.configure import SpiderConfigure
#from dao.mongodao import MongoDAO
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage,PageBasicInfo

from template.templatemanger import TemplateManager
from utility.common import Common
from utility.gettimeutil import getuniformtime
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from utility.xpathutil import XPathUtility

################################################################################################################
# @class：SiteBasicInfo
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class SiteBasicInfo:
    NG_LOG_FORMAT = '{url}\t{name}\t{xpath}\t{value}\tNG'
    OK_LOG_FORMAT = '{url}\t{name}\t{xpath}\t{value}\tOK'
    LOG_FORMAT = '{url}\t{name}\t{xpath}\t{value}\t{result}'    
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
    # @functions：setwebsite
    # @website： 主站
    # @return：none
    # @note：设置主站
    ################################################################################################################
    def setwebsite(self, website):
        self.website = website
    ################################################################################################################
    # @functions：process
    # @param： none
    # @return：none
    # @note：获取网页基本信息
    ################################################################################################################
    def process(self, params):
        # S2 Query Process
        if SPIDER_CHANNEL_S2 == SpiderConfigure.getinstance().getchannel():
            if SPIDER_S2_WEBSITE_TYPE not in params.customized:
                return True
        xparser = XPathUtility(params.content)
        maxitmes = 0
        pageinfo = PageBasicInfo()
        template = None
        for template in TemplateManager.getxpaths(params.url):
            Logger.getlogging().debug(
                'URL_TEMPLATE {url}\t{template}'.format(url=params.url, template=template[TemplateManager.XPATH_KEY_URL_TEMPLATE]))
            pageinfo, items = self.parsefromcontent(params, template, xparser)
            if constant.SPIDER_S2_WEBSITE_TYPE in params.customized:
                pageinfo.type = params.customized[constant.SPIDER_S2_WEBSITE_TYPE]
        #if not params.page_title and not pageinfo.title and not params.lastretry:
            #return False
        if template is None:
            Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
        #值覆盖
        pageinfo.url = params.url
        if not pageinfo.title:
            pageinfo.title = params.page_title
        if not pageinfo.body:
            pageinfo.body = params.page_body
        if not pageinfo.pubtime:
            pageinfo.pubtime = params.html_time        
        NewsStorage.seturlinfos(pageinfo)

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
    

    @staticmethod
    def parsefromcontent(params, template, xparser):
        count = 0
        pageinfo = PageBasicInfo()
        # title
        key = TemplateManager.XPATH_KEY_TITLE
        if template[key].strip():
            title = SiteBasicInfo.xpath(xparser, template[key])
            if title:
                count += 1
                pageinfo.title = title
            else:
                SiteBasicInfo.printxpathinfo(params, key, template[key])
                Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
        elif SiteBasicInfo.xpath(xparser, '//title'):
            count += 1
            pageinfo.title = SiteBasicInfo.xpath(xparser, '//title')
#
        # body
        key = TemplateManager.XPATH_KEY_BODY
        if template[key].strip():
            body = SiteBasicInfo.xpath(xparser, template[key])
            if body:
                count += 1
                pageinfo.body = body
            else:
                SiteBasicInfo.printxpathinfo(params, key, template[key])
                Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
        # 评论量
        key = TemplateManager.XPATH_KEY_COMMENTS_NUM
        pageinfo.cmtnum = SiteBasicInfo.getnum(xparser, template[key], params, key)
        if pageinfo.cmtnum >= 0:
            count += 1
#
        # 阅读量
        key = TemplateManager.XPATH_KEY_CLICK_NUM
        pageinfo.clicknum = SiteBasicInfo.getnum(xparser, template[key], params, key)
        if pageinfo.clicknum >= 0:
            count += 1
#
        # 点赞量
        key = TemplateManager.XPATH_KEY_VOTE_NUM
        pageinfo.votenum = SiteBasicInfo.getnum(xparser, template[key], params, key)
        if pageinfo.votenum >= 0:
            count += 1
#
        # 粉丝量
        key = TemplateManager.XPATH_KEY_FANS_NUM
        pageinfo.fansnum = SiteBasicInfo.getnum(xparser, template[key], params, key)
        if pageinfo.fansnum >= 0:
            count += 1
#
        # 发布时间
        key = TemplateManager.XPATH_KEY_PUBLISH_TIME
        if template[key].strip():
            strpubtime = xparser.getstring(template[key],' ')  #strpubtime = xparser.getstring(template[key])
            pubtime = None
            if strpubtime:
                pubtime = SiteBasicInfo.str2time(strpubtime)
                if pubtime:
                    pageinfo.pubtime = pubtime
                    count += 1
            SiteBasicInfo.printxpathinfo(params, key, template[key], strpubtime, pubtime)
        return pageinfo, count
#
    @staticmethod
    def xpath(xparser, xpath):
        for xp in xpath.split(u'|'):
            value = xparser.getstring(xp, ' ')
            if value.strip():
                return value
        return ''
#
    @staticmethod
    def printxpathinfo(params, name, xpath, value=None, result=None):
        out = SiteBasicInfo.LOG_FORMAT.format(url=params.originalurl,
                                              name=name,
                                              xpath=xpath,
                                              value=SiteBasicInfo.strip(value),
                                              result=result)
        Logger.getlogging().debug(out)
#
    @staticmethod
    def getnum(xparser, xpath, params, name):
        intvalue = -1
        if xpath.strip():
            strvalue = SiteBasicInfo.xpath(xparser, xpath)
            if strvalue:
                if name == TemplateManager.XPATH_KEY_COMMENTS_NUM or name == TemplateManager.XPATH_KEY_CLICK_NUM:
                    intvalue, count = SiteBasicInfo.str2cmtnum(strvalue, name)
                else:
                    intvalue, count = SiteBasicInfo.str2num(strvalue)
            SiteBasicInfo.printxpathinfo(params, name, xpath, strvalue, intvalue)
            if intvalue == -1:
                Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
        return intvalue
#
    UNITS = {u'万': 10000, u'亿': 100000000}
#
    @staticmethod
    def str2num(value):
        value = value.replace(',', '')
        multiplier = 1
        for unit in SiteBasicInfo.UNITS.keys():
            if unit in value:
                multiplier = SiteBasicInfo.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
            res = float(values[0]) * multiplier
        return int(res), len(values)
#
    CMTNUM_FORMATS = [u'\d+条评论',
                      u'\d+个回复',
                      u'\d+条短评',
                      u'回复\(\d+\)',
                      u'评论\(\d+\)',
                      u'评论:\d+',
                      u'评论数:\d+',
                      u'\d+条']
#
    CLICKNUM_FORMATS = [
        u'总点击:\d+',
        u'播放:\d+',
        u'总播放量:\d+',
        u'点击:\d+',
        u'查看:\d+',
        u'点击数:\d+',
        u'点击量:\d+',
        u'浏览次数:约\d+',
        u'阅读\(\d+\)'
    ]
#
    NUMBER_FORMATS = {
        TemplateManager.XPATH_KEY_COMMENTS_NUM: CMTNUM_FORMATS,
        TemplateManager.XPATH_KEY_CLICK_NUM: CLICKNUM_FORMATS
    }
#
    @staticmethod
    def str2cmtnum(value, key):
        value = value.replace(',', '')
        multiplier = 1
        for unit in SiteBasicInfo.UNITS.keys():
            if unit in value:
                multiplier = SiteBasicInfo.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if len(values) == 1:
            res = float(values[0]) * multiplier
        elif len(values) > 1:
            value = SiteBasicInfo.strip(value, '').replace(u'（', '(').replace(u'）', ')').replace(u'：', ':')
            for format in SiteBasicInfo.NUMBER_FORMATS[key]:
                str = RegexUtility.search(format, value)
                if str:
                    res, c = SiteBasicInfo.str2num(str.group(0))
                    break
            else:
                res = float(values[0]) * multiplier
        return int(res), len(values)
#
    @staticmethod
    def strip(value, replace=' '):
        if value:
            return re.sub('[\t\r\n ]+', replace, value)
        else:
            return value
#
    @staticmethod
    def str2time(string):
        return getuniformtime(string)
#

