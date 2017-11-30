# encoding=utf8

##############################################################################################
# @file：Chinavaluecomments.py
# @author：YuXiaoye
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################

import json
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility


##############################################################################################
# @class：Chinavaluecomments
# @author：YuXiaoye
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################
class Chinavaluecomments(SiteComments):
    COMMENT_URL = 'http://app.chinavalue.net/Comment/Comment.ashx?Type={Type}&ObjID={bjID}&PageSize=0'
    STEP_1 = None
    STEP_3_BBS = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：Chinavaluecomments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.offset = 0
        self.limit = 30

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：Chinavaluecomments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Chinavaluecomments.STEP_1:
                self.step1(params)
            elif params.step == Chinavaluecomments.STEP_3_BBS:
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
    # @date：2016/12/2
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        commentinfo_url = None
        Logger.getlogging().info("Chinavaluecomments.STEP_1")
        bjIDs = self.r.parse('^http://www.chinavalue.net/Finance/(\w+?)/.*/(\d+?)\.[aspx|html]', params.originalurl)
        if bjIDs:
            bjID = bjIDs[0][1]
            Types = bjIDs[0][0]
            if Types == 'Article':
                Type = 1
            if Types == 'Blog':
                Type = 2
            # 1. 根据输入原始url, 拼出评论首页
       
            commentinfo_url = Chinavaluecomments.COMMENT_URL.format(Type = Type,bjID=bjID)
        # 评论首页URL
        # 论坛
        if commentinfo_url:
            self.storeurl(commentinfo_url, params.originalurl, Chinavaluecomments.STEP_3_BBS,)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("Chinavaluecomments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        params.content = params.content[1:len(params.content) - 1]
        commentsinfo = json.loads(params.content)
        comments_count = commentsinfo['RecordCount']
        # 判断增量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)

        comments = []
        for index in range(0,len(commentsinfo['CommentObjs'])):
            # 提取时间
            cmti = CommentInfo()
            cmti.content = commentsinfo['CommentObjs'][index]['Content']
            tm = TimeUtility.getuniformtime(TimeUtility.getuniformtime(commentsinfo['CommentObjs'][index]['AddTime'], u'%Y-%m-%d %H:%M'))
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)

        # 保存获取的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)
