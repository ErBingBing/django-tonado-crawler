# encoding=utf-8

##############################################################################################
# @file：baozouvideocomments.py
# @author：Yongjicao
# @date：2016/11/21
# @version：Ver0.0.0.100
# @note：暴走漫画视频频道获取评论的文件
##############################################################r################################

import json
import math
import datetime
import traceback
import time
from lxml import etree

from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.commentsstorage import CommentsStorage
from storage.urlsstorage import URLStorage
from storage.urlsstorage import URLCommentInfo

##############################################################################################
# @class：BaozouVideoComments
# @author：Yongjicao
# @date：2016/11/21
# @note：暴走漫画视频频道获取评论的类，继承于WebSite类
##############################################################################################
class BaozouVideoComments(SiteComments):


    COMMENTS_URL = 'http://baozou.com/api/v2/articles/%d/web_comments?page=%d&per_page=%d'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/11/21
    # @note：BaozouVideoComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.per_page = 100
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    # Step2：获取评论的所有url
    # Step3: 抽出的评论和最新评论的创建时间
    # @author：Yongjicao
    # @date：2016/11/21
    # @note：Step1：通过共通模块传入的html内容获取到article_id，拼出获取评论总数的url，并传递给共通模块
    # Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    # Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################

    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is BaozouVideoComments.STEP_1:
                    # Step1: 通过原始url得到moveid，得到获取评论的首页url。
                    Logger.getlogging().info("proparam.step is None")
                    article_id = int(self.r.parse(r'^http://baozou\.com/\w+/(\d+).*', proparam.url)[0])
                    Logger.getlogging().debug(article_id)

                    commentinfo_url = BaozouVideoComments.COMMENTS_URL % (article_id,1,self.per_page)
                    self.storeurl(commentinfo_url, proparam.originalurl, BaozouVideoComments.STEP_2,{'article_id' : article_id})


            elif proparam.step == BaozouVideoComments.STEP_2:
                # Step2: 通过Step1设置url，得到评论的总数和最后一次评论时间,并根据评论总数得到获取其他评论的url。
                Logger.getlogging().info("proparam.step == 2")
                article_id = proparam.customized['article_id']
                commentsinfo = json.loads(proparam.content)
                #print commentsinfo
                comments_count = int(commentsinfo['total_entries'])
                #print comments_count
                Logger.getlogging().debug('{url} comment: {ct}'.format(url = proparam.url, ct = comments_count))
                #page = commentsinfo['total_pages']
                #print page
                if comments_count == 0:
                    return

                # 拼出获取评论的URL并保存
                for page in range(1, int(math.ceil(float(comments_count) / self.per_page)) + 1, 1):

                    comment_url = BaozouVideoComments.COMMENTS_URL % (article_id,page,self.per_page)
                    self.storeurl(comment_url, proparam.originalurl, BaozouVideoComments.STEP_3)
            elif proparam.step == BaozouVideoComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("proparam.step == 3")
                commentsinfo = json.loads(proparam.content)
                contents = commentsinfo['comments']
                commentsarr = []
                for content in contents:
                    cmti = CommentInfo()
                    tm = TimeUtility.getuniformtime(content['created_at'], '%Y-%m-%d %H:%M:%S')
                    if URLStorage.storeupdatetime(proparam.originalurl, tm):
                        cmti.content = content['content']
                        commentsarr.append(cmti)

                # 保存获取的评论
                if len(commentsarr) > 0:
                    self.commentstorage.store(proparam.originalurl, commentsarr)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=proparam.step))

        except Exception, e:
            traceback.print_exc()