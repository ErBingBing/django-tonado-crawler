# encoding=utf-8
##############################################################################################
# @file：tudoucomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/21
# @note：土豆整站评论获取
##############################################################################################

import json
import math
import urllib
from bsddb import db
from utility.md5 import MD5
from utility.httputil import HttpUtility
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
import traceback
import time
import datetime
from  utility.timeutility import TimeUtility

##############################################################################################
# @class：TudouComments
# @author：Merlin.W.OUYANG
# @date：2016/11/21
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class TudouComments(SiteComments):
    COMMENTS_URL = 'http://p.comments.youku.com/ycp/comment/pc/commentList?objectId=%s&app=100-DDwODVkv' \
                   '&currentPage=%d&pageSize=%d&listType=0&sign=%s&time=%s'
    # PLAYCOUNT_URL = 'http://www.tudou.com/crp/itemSum.action?app=2&showArea=true&iabcdefg={iid}&uabcdefg=0'
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    # STEP_PLAYCOUNT = 'PLAYCOUNT'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date: 2017/9/18
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return: Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date: 2017/9/18
    # @note: Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
    #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
    #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
    #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
    #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
    ##############################################################################################
    def process(self,params):
        try:
            if params.step is TudouComments.STEP_1:
                # 从url中获取拼接评论url的参数
                objectId = self.r.getid('vid', params.content, '\s*:\s*"')
                pTime = str(int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now())) * 1000))
                # 获取参数中的随机数
                sign = MD5().m('100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&' + pTime)
                # 拼接第一页评论url
                comments_url = TudouComments.COMMENTS_URL % (objectId, 1, TudouComments.PAGE_SIZE, sign, pTime)
                # 通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, TudouComments.STEP_2, {'objectId': objectId})


            elif params.step is TudouComments.STEP_2:

                objectId = params.customized['objectId']
                pTime = str(int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now())) * 1000))
                # 获取参数中的随机数
                sign = MD5().m('100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&' + pTime)
                # 获取评论的Jason返回值
                comments = json.loads(params.content)
                # 比较上次抓取该url的页面评论量和当前取到的评论量
                if not comments.has_key('data'):
                    Logger.getlogging().warning("{url}:30000 No comments!".format(url=params.originalurl))
                    return
                if not comments['data']:
                    Logger.getlogging().warning("{url}:30000 No comments!".format(url=params.originalurl))
                    return
                # 判断增量
                comments_count = comments['data']['totalSize']
                cmtnum = CMTStorage.getcount(params.originalurl,True)
                if int(comments_count <= cmtnum):
                    return
                NewsStorage.setcmtnum(params.originalurl,comments_count)

                # 获取评论总页数
                comments_pages = int(comments['data']['totalPage'])
                if comments_pages == 0:
                    return
                # 如果评论数量过多只取前十页
                if comments_pages >= self.maxpages:
                    comments_pages = self.maxpages

                lasttime = CMTStorage.getlastpublish(params.originalurl, True)
                # 循环拼接评论url，提交下载平台获取评论数据
                for page in range(0, comments_pages + 1, 1):
                    commentUrl = TudouComments.COMMENTS_URL % (objectId, page + 1,  TudouComments.PAGE_SIZE, sign, pTime)
                    self.storeurl(commentUrl, params.originalurl,  TudouComments.STEP_3, {'objectId': objectId})

            elif params.step is TudouComments.STEP_3:
                commentsinfo = json.loads(params.content)
                for comment in commentsinfo['data']['comment']:
                    content = comment['content']
                    curtime = TimeUtility.getuniformtime(int(comment['createTime']))
                    nick = comment['user']['userName']
                    # 通过时间判断评论增量
                    # if curtime > lasttime:
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()