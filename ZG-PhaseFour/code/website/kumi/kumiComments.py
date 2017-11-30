# encoding=utf-8
##############################################################################################
# @file：kumiComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：酷米网获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################

from website.common.comments import SiteComments
from website.common.changyanComments import ChangyanComments
from log.spiderlog import Logger
import re
from storage.newsstorage import NewsStorage
import json

##############################################################################################
# @class：kumiComments
# @author：Liyanrui
# @date：2016/11/18
# @note：酷米网获取评论的类，继承于SiteComments类
##############################################################################################
class kumiComments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：酷米网类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.changyan = None
        self.STEP_TVCLICK = 'tvclick'
        # http: // list.kumi.cn / num.php?contentid = 87056
        self.VIDEO_CLICKURL = 'http://list.kumi.cn/num.php?contentid ={contentid}'
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        # if NewsStorage.getclicknum(proparam.originalurl) <= 0:
        #     contentid = self.r.parse('^http://www\.kumi\.cn/(\w+)/(\d+)(_\d)?\.html.*', proparam.originalurl)[1]
        #     clickurl = self.VIDEO_CLICKURL.format(contentid=contentid)
        #     self.storeurl(clickurl, proparam.originalurl, self.STEP_TVCLICK)

        try:
            if self.r.search('^http://.*\.kumi\.cn/.*',proparam.originalurl):
                contentid = self.r.parse('^http://www\.kumi\.cn/(\w+)/(\d+)(_\d)?\.html.*', proparam.originalurl)[1]
                clickurl = self.VIDEO_CLICKURL.format(contentid=contentid)
                self.storeurl(clickurl, proparam.originalurl, self.STEP_TVCLICK)
                if 'donghua' in proparam.originalurl:
                    topicSourceId = re.findall(r'^http://www\.kumi\.cn/donghua/(\d+)(_\d)?\.html',
                                               proparam.originalurl).__getitem__(0).__getitem__(0)
                else:
                    topicSourceId = re.findall(r'^http://xiaoyouxi\.kumi\.cn/(\d+)(_\d)?\.htm',
                                               proparam.originalurl).__getitem__(0).__getitem__(0)
                self.createobject().getcomments(proparam, topicSourceId, 3, 2)
            elif proparam.setp == self.STEP_TVCLICK :
                self.setclicknum_tv(proparam)



        except:
            Logger.printexception()

    def createobject(self):
        if self.changyan is None:
             self.changyan = ChangyanComments(self)
        return self.changyan
    def setclicknum_tv(self, proparam):
        jsondate = json.loads(proparam.content)
        todayplaynum = 222
        NewsStorage.setclicknum(proparam.originalurl, todayplaynum)

