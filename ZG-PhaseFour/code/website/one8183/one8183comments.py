# encoding=utf-8
##############################################################################################
# @file：Game3dmComments.py
# @author：yongjicao
# @date：2016/12/08
# @version：Ver0.0.0.100
# @note：3dmgame网获取评论的文件
###############################################################################################

from website.common.comments import SiteComments
from utility.bbs2commom import CommenComments
from website.common.changyanComments import ChangyanComments
from log.spiderlog import Logger
from utility.xpathutil import XPathUtility
from utility.gettimeutil import getuniformtime

from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import TimeUtility
import time
import re

##############################################################################################
# @class：Game3dmComments
# @author：yongjicao
# @date：2016/12/08
# @note：3dmgame网获取评论的类，继承于SiteComments类
##############################################################################################
class One8183Comments(SiteComments):

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：yongjicao
    # @date：2016/12/06
    # @note：3dmgame网类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.changyan = None

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：yongjicao
    # @date：2016/12/08
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        field = self.r.parse('^http://(\w+)\.18183\.com*', params.originalurl)[0]
        if field == 'bbs':
            CommenComments.getinstance(self).process(params)
        else:
            ChangyanComments(self).getcomments(params, '', 3, 2)
        #重新设置部分网页的putime
        if field == 'chanye':
            self.setpubtime(params)
    
    def setpubtime(self, params):
        newtime = None
        if re.search('http://chanye\.18183\.com/.*',params.url):
            Xhtml = XPathUtility(params.content)
            timestr = Xhtml.getstring('//*[@class="arc-other"]/span[3]|//*[@class="other"]/span[3]')    
            if not timestr:
                return
            p = '(\d{2}-\d+-\d+)'
            if re.search(p,timestr):
                new = str(time.localtime()[0])[0:2] + re.findall(p,timestr)[0]
                newtime = getuniformtime(new)
        #if re.search('http://bbs\.18183\.com/.*',params.url):
            #Xhtml = XPathUtility(params.content)
            #timestr = Xhtml.getstring('//*[@class="authi"]/em')
            #if not timestr:
                #return
            #times = timestr.split(u'发表于')[1]
            #newtime = TimeUtility.getuniformtime(times)
        if newtime:
            NewsStorage.setpublishdate(params.originalurl,newtime)
