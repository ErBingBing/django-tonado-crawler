# encoding=utf8

##############################################################################################
# @file：ThirtysixKryptonComments.py
# @author：Liuyonglin
# @date：2016/12/8
# @version：Ver0.0.0.100
# @note：36氪创业资讯页获取评论的文件
##############################################################################################

import json
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility


##############################################################################################
# @class：ThirtysixKryptonComments
# @author：Liuyonglin
# @date：2016/12/8
# @version：Ver0.0.0.100
# @note：36氪创业资讯页获取评论的文件
##############################################################################################
class ThirtysixKryptonComments(SiteComments):
    COMMENT_URL = 'http://36kr.com/api/comment?cid={0}&ctype=post&per_page={1}&page={2}'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liuyonglin
    # @date：2016/12/8
    # @note：ThirtysixKryptonComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 30

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/8
    # @note：ThirtysixKryptonComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is ThirtysixKryptonComments.STEP_1:
                self.step1(params)
            elif params.step == ThirtysixKryptonComments.STEP_2:
                self.step2(params)
            elif params.step == ThirtysixKryptonComments.STEP_3:
                self.step3(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/8
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("ThirtysixKryptonComments.STEP_1")
        cid = self.r.parse('^http://36kr.com/p/(\d+)\.html', params.originalurl)[0]
        # 根据输入原始url, 拼出评论首页
        commentinfo_url = ThirtysixKryptonComments.COMMENT_URL.format(cid, self.page_size, 1)
        self.storeurl(commentinfo_url, params.originalurl, ThirtysixKryptonComments.STEP_2,{'cid':cid})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/8
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("ThirtysixKryptonComments.STEP_2")
        # 将STEP_1中的cid传下来
        cid = params.customized['cid']

        jsoncontent = json.loads(params.content)
        comments_count = jsoncontent['data']['total_items']
        page_count = jsoncontent['data']['total_pages']

        # 判断增量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)

        for page in range(1, page_count+1, 1):
            commentinfo_url = ThirtysixKryptonComments.COMMENT_URL.format(cid, self.page_size, page)
            self.storeurl(commentinfo_url, params.originalurl, ThirtysixKryptonComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/8
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("ThirtysixKryptonComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        jsoncontent = json.loads(params.content)
        commentsInfo = []

        for index in range(0, len(jsoncontent['data']['items']), 1):
            cmti = CommentInfo()
            # 提取评论内容
            cmti.content = jsoncontent['data']['items'][index]['content']
            # 提取时间
            publicTime = jsoncontent['data']['items'][index]['created_at']
            tm = TimeUtility.getuniformtime(TimeUtility.getuniformtime(publicTime, u'%Y-%m-%d %H:%M:%S'))
            if URLStorage.storeupdatetime(params.originalurl, tm):
                commentsInfo.append(cmti)

        if len(commentsInfo) > 0:
            # 保存获取的评论
            self.commentstorage.store(params.originalurl, commentsInfo)