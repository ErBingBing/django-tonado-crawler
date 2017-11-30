# encoding=utf8

##############################################################################################
# @file：BaozouNewsComments.py
# @author：YuXiaoye
# @date：2016/12/6
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################

import json
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility
from utility.gettimeutil import getuniformtime
from utility.timeutility import TimeUtility
import datetime

##############################################################################################
# @class：BaozouNewsComments
# @author：YuXiaoye
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################
class BaozouNewsComments(SiteComments):
    COMMENT_URL = 'http://baozou.com/api/v2/articles/{topic_id}/web_comments?page={page}'
    STEP_1 = None
    STEP_2_BBS = '2'
    STEP_3_BBS = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：BaozouNewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/12
    # @note：BaozouNewsComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is BaozouNewsComments.STEP_1:
                self.step1(params)
            elif params.step == BaozouNewsComments.STEP_2_BBS:
                self.step2bbs(params)
            elif params.step == BaozouNewsComments.STEP_3_BBS:
                self.step3bbs(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/12
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("BaozouNewsComments.STEP_1")
        topic_id = self.r.parse('^http://baozou.com/articles/(\d+).*', params.originalurl)[0]
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = BaozouNewsComments.COMMENT_URL.format(topic_id=topic_id,page = 1)
        self.storeurl(commentinfo_url, params.originalurl, BaozouNewsComments.STEP_2_BBS,{'topic_id':topic_id})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/12
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("BaozouNewsComments.STEP_2")
        topic_id = params.customized['topic_id']
        commentsinfo = json.loads(params.content)
        comments_count = commentsinfo['total_count']
        # 保存页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)
        for index in range(1, int(commentsinfo['total_pages']) + 1, 1):
            commentinfo_url = BaozouNewsComments.COMMENT_URL.format(topic_id = topic_id,page = index)
            self.storeurl(commentinfo_url, params.originalurl, BaozouNewsComments.STEP_3_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/12
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("BaozouNewsComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        commentsinfo = json.loads(params.content)
        comments = []
        for index in range(0, int(len(commentsinfo['comments'])), 1):
            # 提取时间
            cmti = CommentInfo()
            cmti.content = commentsinfo['comments'][index]['content']
            tm = commentsinfo['comments'][index]['created_at']
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)

        # 保存获取的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)
