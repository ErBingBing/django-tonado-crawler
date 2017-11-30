# coding=utf-8

################################################################################################################
# @file: site.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import re
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from storage.urlmanager import URLContext, URLManager
from utility.timeutility import TimeUtility
# from website.common.basicinfo import SiteBasicInfo
from website.common.basicinfo import SiteBasicInfo 
################################################################################################################
# @class：WebSite
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
#from website.common.s1basic import SiteS1Basic


class WebSite:

    # default pattern, no match any site
    DEFAULT_PATTERN = 'no site match me'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：WebSite，初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.name = 'WebSite'
        self.pattern = WebSite.DEFAULT_PATTERN
        self.patterns = []
        # self.basic = SiteBasicInfo()
        # self.__s1basicimpl = SiteS1Basic()
        self.__s1basicimpl = SiteBasicInfo()
        self.__s2queryimpl = None
        self.__s3extractimpl = None
        self.__comments = None
        self.commentstorage = None

    ################################################################################################################
    # @functions：process
    # @url 真实URL
    # @params.url 同url
    # @params.content html或者json数据
    # @params.originalurl 原始URL（新闻页或者视频URL）
    # @params.step
    # @params.customized 用户自定义参数
    # @return：none
    # @note：网页处理逻辑，分配给不同的基本信息类、评论类处理
    ################################################################################################################
    def addpattern(self, pattern):
        self.patterns.append(pattern)

    ################################################################################################################
    # @functions：process
    # @url 真实URL
    # @params.url 同url
    # @params.content html或者json数据
    # @params.originalurl 原始URL（新闻页或者视频URL）
    # @params.step
    # @params.customized 用户自定义参数
    # @return：none
    # @note：网页处理逻辑，分配给不同的基本信息类、评论类处理
    ################################################################################################################
    def process(self, params):
        res = True
        Logger.getlogging().info(params.url)
        try:
            #if params.type == URLContext.S3_HOME_PAGE:
                #if self.__s3extractimpl:
                    #self.__s3extractimpl.process(params)
            if params.type == URLContext.S2_QUERY:
                if self.__s2queryimpl is not None:
                    self.__s2queryimpl.process(params)
            elif params.type == URLContext.S1_MAIN_BODY:
                if self.__s1basicimpl:
                    self.__s1basicimpl.process(params)
                if self.__comments is not None:
                    self.__comments.process(params)
            elif params.type == URLContext.S1_COMMENTS:
                if self.__comments is not None:
                    self.__comments.process(params)
            else:
                Logger.getlogging().warning(params.url)
        except:
            Logger.printexception()
        Logger.getlogging().info(params.url)
        return res

    ################################################################################################################
    # @functions：storeurl
    # @url 真实URL
    # @originalurl 网页url
    # @step 当该网页内存返回时，处理标识
    # @customized 下一步处理对当前处理的依赖，字典类型
    # @return：none
    # @note：将新生成URL输出到文件，同时记录原始URL与新生成的URL对应关系
    ################################################################################################################
    def storeurl(self, url, originalurl, step, customized={}):
        urlparam = URLContext()
        urlparam.url = url
        urlparam.originalurl = originalurl
        urlparam.step = step
        urlparam.customized = customized
        URLManager.getinstance().storeurl(url, urlparam)

    ################################################################################################################
    # @functions：match
    # @url URL
    # @return：return True if match else False
    # @note：判断URL是否跟模板匹配
    ################################################################################################################
    def match(self, url):
        if len(self.patterns) > 0:
            for pattern in self.patterns:
                if re.match(pattern, url):
                    return True
        else:
            return re.match(self.pattern, url)
        return False

    ################################################################################################################
    # @functions：sets1basicimpl
    # @impl S2Query Class instance
    # @note：设置S2Query类实例
    ################################################################################################################
    def sets1basicimpl(self, impl):
        self.__s1basicimpl = impl
        self.__s1basicimpl.setwebsite(self)

    ################################################################################################################
    # @functions：sets2queryimpl
    # @impl S2Query Class instance
    # @note：设置S2Query类实例
    ################################################################################################################
    def sets2queryimpl(self, impl):
        self.__s2queryimpl = impl
        self.__s2queryimpl.setwebsite(self)

    ################################################################################################################
    # @functions：sets2extractimpl
    # @impl S2Extract Class instance
    # @note：设置S3Extract类实例
    ################################################################################################################
    def sets3extractimpl(self, impl):
        self.__s3extractimpl = impl
        self.__s3extractimpl.setwebsite(self)

    ################################################################################################################
    # @functions：setcommentimpl
    # @impl Comment Class instance
    # @note：设置Comments类实例
    ################################################################################################################
    def setcommentimpl(self, impl):
        self.__comments = impl
        self.__comments.setwebsite(self)

    ################################################################################################################
    # @functions：s2query
    # @info query条件
    # @note：S2 query
    ################################################################################################################
    def s2query(self, info):
        if self.__s2queryimpl is not None:
            self.__s2queryimpl.query(info)

    ################################################################################################################
    # @functions：exists2
    # @param none
    # @retrun True for __s2queryimpl is not none, else False
    # @note：S2 query
    ################################################################################################################
    def exists2(self):
        return self.__s2queryimpl is not None

################################################################################################################
# @class：ProcessParam
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：WebSite().prcoess方法的参数
################################################################################################################
class ProcessParam:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：ProcessParam初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 真实URL
        self.url = ''
        # 处理真实URL内容的步骤名称
        self.step = None
        # 真实URL对应的内容
        self.content = ''
        # 真实URL对应的原始URL
        self.originalurl = ''
        # 自定义参数
        self.customized = {}
        # 页面爬取时间
        self.crawler_time = ''
        # page_title
        self.page_title = ''
        # page_body
        self.page_body = ''
        # html_time
        self.html_time = ''
        # post data
        self.data = {}
        # lastretry
        self.lastretry = False

    ################################################################################################################
    # @functions：parseinfofromjson
    # @jsondata： 下载平台得到的json数据
    # @return：none
    # @note：从json数据中获取相应的字段
    ################################################################################################################
    def parseinfofromjson(self, jsondata):
        # 页面爬取时间
        self.crawler_time = TimeUtility.getuniformtime2(int(jsondata['crawler_time']))
        # get title/body
        properties = jsondata['property']
        for property in properties:
            if property['property_name'] == 'page_title':
                self.page_title = property['result'][0]['text']
            elif property['property_name'] == 'page_body':
                self.page_body = property['result'][0]['text']

