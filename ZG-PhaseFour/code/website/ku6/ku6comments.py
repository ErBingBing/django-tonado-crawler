# coding=utf-8
##############################################################################################
# @file：ku6comments.py
# @author：Ninghz
# @date：2016/11/20
# @note：酷6视频网站获取评论的文件
##############################################################################################

import json
import datetime
import traceback
import math

from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from website.common.changyanComments import ChangyanComments

##############################################################################################
# @class：ku6Comments
# @author：Ninghz
# @date：2016/11/20
# @note：酷6视频网站获取评论的类，继承于SiteComments类
##############################################################################################
class Ku6Comments(SiteComments):
    COMMENTS_URL = 'http://comment.ku6.com/api/list.jhtm?id=%s&vtype=111&type=2&size=%d&pn=%d'
    COMMENTS_SOURCE_URL = 'http://changyan.sohu.com/api/3/topic/liteload?client_id={0}&topic_source_id={1}&page_size={2}'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/11/20
    # @note：ku6Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()
        self.client_id = 'cytaCBUri'
        # self.basicstorage = BaseInfoStorage()
        # self.commentstorage = CommentsStorage()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/11/20
    # @note：Step1：通过共通模块传入的html内容获取到oid，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                # 从url中获取拼接评论url的参数
                oid = self.r.parse('^http://v\.ku6\.com/show/([\w-]+..).html', params.originalurl)[0]
                # 拼接第一页评论url
                comments_url = Ku6Comments.COMMENTS_URL % (oid, 1, 1)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, Ku6Comments.STEP_2, {'oid': oid})

            #获取第一页评论内容，循环获取全部评论url
            elif params.step == Ku6Comments.STEP_2:
                oid = params.customized['oid']
                # 获取评论的Jason返回值
                comments = json.loads(params.content)

                # 获取评论总数
                comments_count = float(comments['data']['count'])
                NewsStorage.setcmtnum(params.originalurl, int(comments['data']['count']))
                if comments_count == 0:
                    return
                # 比较上次抓取该url的页面评论量和当前取到的评论量
                cmtnum = CMTStorage.getcmtnum(params.originalurl,True)
                if cmtnum >= comments_count:
                    return
                # 循环拼接评论url，提交下载平台获取评论数据
                for page in range(0, int(math.ceil(comments_count / Ku6Comments.PAGE_SIZE)) + 1, 1):
                    commentUrl = Ku6Comments.COMMENTS_URL % (oid, Ku6Comments.PAGE_SIZE, page + 1)
                    self.storeurl(commentUrl, params.originalurl, Ku6Comments.STEP_3, {'oid': oid})


            #解析评论数据
            elif params.step == Ku6Comments.STEP_3:
                commentsinfo = json.loads(params.content)
                if not commentsinfo['data']['list']:
                    return
                for comment in commentsinfo['data']['list']:
                    curtime = TimeUtility.getuniformtime(int(comment['commentCtime']))
                    content = comment['commentContent']
                    nick = comment['commentContent']
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)


        except Exception, e:
            Logger.printexception()
