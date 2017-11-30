# encoding=utf-8
##############################################################################################
# @file：chinabytecomments.py
# @author：Merlin.W.OUYANG
# @date：2016/12/6
# @note：评论获取,使用的是第三方多说的cms插件
# @modify
# @author:Jiangsiwei
# @date:2017/02/07
# @note:第75到81行，添加了对请求数据不是json文件时的异常处理
##############################################################################################

import json
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from utility.gettimeutil import getuniformtime

##############################################################################################
# @class：ChinabyteComments
# @author：Merlin.W.OUYANG
# @date：2016/12/6
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class ChinabyteComments(SiteComments):
    COMMENTS_URL = 'http://chinabyte.duoshuo.com/api/threads/listPosts.json?thread_key=%s&page=%d&order=desc'
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/12/6
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        #self.r = RegexUtility()
        #self.basicstorage = BaseInfoStorage()
        #self.commentstorage = CommentsStorage()

        #----------------------------------------------------------------------
        ##############################################################################################
        # @functions：process
        # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
        # @return：Step1：获取评论的首页url
        #          Step2：获取评论的所有url
        #          Step3: 抽出的评论和最新评论的创建时间
        # @author：Merlin.W.ouyang
        # @date：2016/12/6
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
        #               获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
        #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
        #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
        #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
        ##############################################################################################   

    def process(self, params):
        try:
            if params.step is ChinabyteComments.STEP_1:
                threadid = self.r.parse('data-thread-key=\"(.*?)\"',params.content)
                if not threadid:
                    return
                comments_url = ChinabyteComments.COMMENTS_URL % (threadid[0], 1)
                self.storeurl(comments_url, params.originalurl, ChinabyteComments.STEP_2, {'threadid':threadid[0],'pageno':1})

            elif params.step == ChinabyteComments.STEP_2:
                try:
                    threadid = params.customized['threadid']
                    comments = json.loads(params.content)       
                    pagetotal= int(comments['cursor']['pages'])      
                except:
                    Logger.getlogging().warning('{0}:30000'.format(params.originalurl))
                    return
                #threadid = params.customized['threadid']
                #comments = json.loads(params.content)       
                #pagetotal= int(comments['cursor']['pages']) 
                # pages==0的场合，没有评论
                if pagetotal == 0:
                    return
                for page in range(1, pagetotal+1, 1):
                    comments_url = ChinabyteComments.COMMENTS_URL % (threadid,page)
                    self.storeurl(comments_url, params.originalurl, ChinabyteComments.STEP_3)
            #     comments_url = ChinabyteComments.COMMENTS_URL % (params.customized['threadid'],params.customized['pageno'])
            #     self.storeurl(comments_url, params.originalurl, ChinabyteComments.STEP_3,
            #                   {'threadid':params.customized['threadid'],
            #                    'pageno':params.customized['pageno'],
            #                    'totalpage':pagetotal})
            #
            elif params.step == ChinabyteComments.STEP_3:
                comments = []
                commentinfo = json.loads(params.content)
                for key in commentinfo['parentPosts'].keys():
                    updatetime = getuniformtime(commentinfo['parentPosts'][key]['created_at'])
                    if URLStorage.storeupdatetime(params.originalurl, updatetime):
                        cmti = CommentInfo()
                        cmti.content = commentinfo['parentPosts'][key]['message']
                        comments.append(cmti)
                if len(comments) > 0:
                    self.commentstorage.store(params.originalurl, comments)
        except:
            Logger.printexception()