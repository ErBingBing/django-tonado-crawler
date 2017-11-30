# coding=utf-8
##############################################################################################
# @file：cine107comments.py
# @author：Ninghz
# @date：2016/11/25
# @note：影视工业网"论坛广场"获取评论的文件
##############################################################################################

import json
import datetime
import traceback
import math


from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.basicinfostorage import BaseInfoStorage
from storage.commentsstorage import CommentsStorage
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from log.spiderlog import Logger
from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility


##############################################################################################
# @class：Cine107Comments
# @author：Ninghz
# @date：2016/11/25
# @note：影视工业网"论坛广场"获取评论的类，继承于SiteComments类
##############################################################################################
class Cine107Comments(SiteComments):
    COMMENTS_URL = '{url}?order=desc&page={pageno}'
    PAGE_SIZE = 15.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/11/25
    # @note：Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()
        self.basicstorage = BaseInfoStorage()
        self.commentstorage = CommentsStorage()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/11/25
    # @note：Step1：通过共通模块传入的html内容获取到operaId，contentId，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                # 根据html内容获取评论总数
                xhtml = XPathUtility(html=params.content)
                countsStr = str(xhtml.getstring('//*[@id="chartForm"]/div[1]/a[3]'))
                startpos = countsStr.find('(')
                if startpos < 0:
                    Logger.getlogging().error(params.originalurl)
                    return
                comment_counts = int(countsStr[startpos+1:countsStr.find(')')])
                Logger.getlogging().debug(comment_counts)
                if comment_counts == 0:
                    return
                # 比较上次抓取该url的页面评论量和当前取到的评论量
                #
                # 循环拼接评论url，提交下载平台获取评论数据
                for page in range(1, int(math.ceil(comment_counts/Cine107Comments.PAGE_SIZE)) + 1, 1):
                    commentUrl = Cine107Comments.COMMENTS_URL.format(url=params.originalurl, pageno=page)
                    Logger.getlogging().debug(commentUrl)
                    self.storeurl(commentUrl, params.originalurl, Cine107Comments.STEP_2)
                URLStorage.setcmtnum(params.originalurl, comment_counts)

            #解析评论数据
            elif params.step == Cine107Comments.STEP_2:
                xhtml = XPathUtility(html=params.content)
                comments = []
                contents = xhtml.getlist('//*[@class="flow_commont_list clearfix"]/p')
                updatetimes = xhtml.getlist('//*/time')
                for index in range(0, len(contents), 1):
                    udpatetime = TimeUtility.getuniformtime(updatetimes[index])
                    if URLStorage.storeupdatetime(params.originalurl, udpatetime):
                        cmti = CommentInfo()
                        Logger.getlogging().debug(contents[index])
                        cmti.content = str(contents[index])
                        comments.append(cmti)
                    if len(comments) > 0:
                        self.commentstorage.store(params.originalurl, comments)
        except:
            Logger.printexception()