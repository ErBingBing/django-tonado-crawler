# coding=utf8
################################################################################################################
# @file: comments.py
# @author: Jiang Siwei
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import json
import urllib
import re
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from storage.urlmanager import URLManager, URLContext
from utility import const
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage

################################################################################################################
# @class：SiteComments
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class SiteComments:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SiteBasicInfo初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.r = RegexUtility()
        self.website = None
        self.cmtlastdays = TimeUtility.getuniformdatebefore(delta=int(SpiderConfigure.getinstance().getlastdays()))[:10] + u' 00:00:00'
        self.maxpages = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN,
                                                      const.SPIDER_S1_MAX_COMMENT_PAGES))

    ################################################################################################################
    # @functions：process
    # @param： ProcessParam参数,site。py
    # @return：none
    # @note：评论处理逻辑
    ################################################################################################################
    def process(self, params):
        pass

    ################################################################################################################
    # @functions：__init__
    # @param： url 需要下载的URL
    # @param： originalurl 网页URL
    # @param： step 处理url的步骤
    # @param： other 其他参数，字典类型
    # @return：none
    # @note：保需要下载的页面
    ################################################################################################################
    def storeurl(self, url, originalurl, step, others={}):
        urlparam = URLContext()
        urlparam.url = url
        urlparam.originalurl = originalurl
        urlparam.step = step
        urlparam.type = URLContext.S1_COMMENTS
        urlparam.customized = others
        URLManager.getinstance().storeurl(url, urlparam)

    ################################################################################################################
    # @functions：__init__
    # @param： url 需要下载的URL
    # @param： originalurl 网页URL
    # @param： step 处理url的步骤
    # @param： data POST的参数
    # @param： other 其他参数，字典类型
    # @return：none
    # @note：保需要下载的页面
    ################################################################################################################
    def storeposturl(self, url, originalurl, step, data, others={}):
        urlcontext = URLContext()
        urlcontext.url = json.dumps({'url': url, 'data': urllib.urlencode(data)})
        urlcontext.originalurl = originalurl
        urlcontext.step = step
        urlcontext.type = URLContext.S1_COMMENTS
        urlcontext.customized = others
        URLManager.getinstance().storeurl(urlcontext.url, urlcontext, constant.REQUEST_TYPE_POST)
    ################################################################################################################
    # @functions：setwebsite
    # @website： 主站
    # @return：none
    # @note：设置主站
    ################################################################################################################
    def setwebsite(self, website):
        self.website = website
    
    ################################################################################################################
    # @functions：comparepublish
    # @params: url, time 
    # @return：True  or False
    # @note：比较当前发布时间和数据中中的发布时间,如果当时时间大于以前时间，返回True，否则返回False
    ################################################################################################################
    def isnewesttime(self, url, curtime):
        if curtime > CMTStorage.getlastpublish(url):
            return True
        return False
    
    ################################################################################################################
    # @functions：strfilter
    # @params: string
    # @return：清洗后的字符串
    # @note：
    ################################################################################################################        
    def strfilter(self, s):
        left = 0
        right = 0
        s1 = '<'
        s2 = '>'
        spicial = ['\n','\r','<<','>>']
        for s1 in spicial:
            s = s.replace(s1,' ').strip()       
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
    
    ################################################################################################################
    # @functions：str2num
    # @params: string
    # @return：number
    # @note：
    ################################################################################################################ 
    UNITS = {u'万': 10000, u'亿': 100000000}
    def str2num(self, value):
        value = value.replace(',', '')
        multiplier = 1
        for unit in self.UNITS.keys():
            if unit in value:
                multiplier = self.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
            res = float(values[0]) * multiplier
        return int(res) 