# encoding=utf8

##############################################################################################
# @file：JoyComments.py
# @author：YuXiaoye
# @date：2016/12/14
# @version：Ver0.0.0.100
# @note：着迷网获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################################################

import json
import traceback
import math
from website.common.comments import SiteComments
from log.spiderlog import Logger
# from storage.commentsstorage import CommentInfo
# from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：JoyComments
# @author：YuXiaoye
# @date：2016/12/14
# @version：Ver0.0.0.100
# @note：着迷网获取评论的文件
##############################################################################################
class JoyComments(SiteComments):
    COMMENT_URL = 'http://api.joyme.com/jsoncomment/reply/query?unikey={topic_id}&domain={domain}&pnum={page}&psize=10'
    STEP_1 = None
    STEP_2_BBS = '2'
    STEP_3_BBS = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：JoyComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：JoyComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is JoyComments.STEP_1:
                self.step1(params)
            elif params.step == JoyComments.STEP_2_BBS:
                self.step2bbs(params)
            elif params.step == JoyComments.STEP_3_BBS:
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
    # @date：2016/12/14
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("JoyComments.STEP_1")
        topic_id = self.r.parse('^http://.*/\d\d(\d+).html', params.originalurl)[0]
        webcache = self.r.parse('<script src="http://(\w+).joyme.com/js/comment.js',params.content)
        if len(webcache) != 0:
            domain = 2
        else:
            domain = 6
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = JoyComments.COMMENT_URL.format(topic_id = topic_id, domain = domain, page = 1 )
        self.storeurl(commentinfo_url, params.originalurl, JoyComments.STEP_2_BBS,{'topic_id':topic_id, 'domain':domain})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("JoyComments.STEP_2")
        topic_id = params.customized['topic_id']
        domain = params.customized['domain']
        try:
            commentsinfo = json.loads(params.content)
            comments_count = commentsinfo['result']['mainreplys']['page']['totalRows']
            NewsStorage.setcmtnum(params.originalurl, comments_count)
        except:
            Logger.getlogging().warning('{url} Errorcode:40000'.format(url=params.originalurl))
            #Logger.printexception()
            return 
        # 保存页面评论量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        # 计算增量
        if cmtnum >= comments_count:
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        for index in range(1, page_num + 1, 1):
            commentinfo_url = JoyComments.COMMENT_URL.format(topic_id = topic_id, domain = domain, page = index )
            self.storeurl(commentinfo_url, params.originalurl, JoyComments.STEP_3_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/14
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("JoyComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        try:
            commentsinfo = json.loads(params.content)
            commentsinfo['result']['mainreplys']['rows']
        except:
            Logger.getlogging().warning('{url} Errorcode:40000'.format(url=params.originalurl))
            Logger.printexception()
            return
        # 获取评论
        for index in range(0, int(len(commentsinfo['result']['mainreplys']['rows'])), 1):
            # 提取时间
            # cmti = CommentInfo()
            content = commentsinfo['result']['mainreplys']['rows'][index]['reply']['reply']['body']['text']
            curtime = TimeUtility.getuniformtime(str(commentsinfo['result']['mainreplys']['rows'][index]['reply']['reply']['post_time']))
            nick = commentsinfo['result']['mainreplys']['rows'][index]['reply']['user']['name']
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

