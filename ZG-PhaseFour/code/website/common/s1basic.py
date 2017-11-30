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
import re
from configuration import constant
from dao.mongodao import MongoDAO
from storage.newsstorage import NewsStorage
from utility.regexutil import RegexUtility
from utility.gettimeutil import getuniformtime
from website.common.basicinfo import SiteBasicInfo 

################################################################################################################
# @class：SiteBasicInfo
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from storage.urlmanager import URLManager, URLContext
from utility.xpathutil import XPathUtility

class SiteS1Basic:
    SITEPATTERN = 'sitepattern'
    IMGPATTERNS = 'imgpatterns'
    SPECIALSITEIMG = []
    IMGCOMMONPATTERNS = []    
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
        SiteBasicInfo().process(params)

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
    

    ################################################################################################################
    # @functions：getmedia过滤掉获取来源字段
    # @params：
    # @return：
    # @note：对media获取内容进行过滤掉
    ################################################################################################################    
    @staticmethod
    def getmedia(string):
        #print string
        patterns = [
            u'document\.write\([\"|\'].*来源:([^"].*)[\"|\']\)',
            u'document\.write\([\"|\'].*来源：([^"].*)[\"|\']\)',
            u'var laiyuan.*=.*\'(.*)\'',
            u'var laiyuan.*=.*\"(.*)\";',
            u'var ly.*=.*\'(.*)\';',
            u'var ly=\"(.*)\";',
            u'var source=\'(.*)\';',
            u'发布机构：(.*)',
            u'来源:(.*)',
            u'来源：([\s\S]*)',
            u'【来源】(.*)',
            u'str_1.*=.*\"(.*)\"'
        ]

        others = [u'(.*)关于','(.*)\d{4}.*\d{,2}.*\d{,2}',u'(.*)责任编辑',u'(.*)作者']
        #others = ['(.*)\d{4}.*\d{,2}.*\d{,2}']
        for pattern in patterns:
            if re.search(pattern,string):
                new = re.findall(pattern,string)[-1]
                break
        else:
            new = string
        for other in others:
            if re.search(other,new):
                new = re.findall(other,new)[0]
        new = new.strip()
        #可以直接替换掉的字符串
        special = [u'【',u'】',u'〖',u'〗','[',']','(',')',u'〔',u'）',u'，',u':',u'：',
                   u'发布人',u'发布',u'发文时间',u'日期',u'时间',u'浏览次数',u'浏览量','</span>']
        for s in special:
            new = new.replace(s,'')   
        #需要替换成' '的字符串
        special = ['\n','\r','\t']
        for s in special:
            new = new.replace(s,' ')
        new = new.strip()
        special2 = [' ','|',u'\xa0\xa0',u'\u3000']
        for s in special2:
            new = new.split(s)[0]
        return new
    ################################################################################################################
    # @functions：getimage
    # @params：
    # @return：
    # @note：过滤和获取图片
    ################################################################################################################    
    def getimage(self, imglist,params,imgpatternothers=[],specialsiteimg=[]):
        return ''
    #----------------------------------------------------------------------
    ################################################################################################################
    # @functions：fileterimg
    # @params：
    # @return：
    # @note：对图片的链接进行处理
    ################################################################################################################       
    def fileterimg(self, image, originalurl):
        return ''
    ################################################################################################################
    # @functions：filterstr
    # @params：
    # @return：
    # @note：对字符串进行过滤处理
    ################################################################################################################               
    def filterstr(self, s):
        left = 0
        right = 0
        s1 = '<'
        s2 = '>'
        spicial = ['\t','\n','\r','<<','>>',' ']
        for s1 in spicial:
            s = s.replace(s1,'')         
        while True:
            if s1 not in s or s2 not in s:
                break            
            if s1 in s: 
                left = s.index(s1)
            if s2 in s:
                right = s.index(s2)      
            if right:
                s = s.replace(s[left:right+1],'')
        return s
