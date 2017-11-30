# encoding=utf-8
##############################################################################################
# @file：pcgamescomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/18
# @note：环球财讯网国内财讯页评论获取,使用的是第三方多说的cms插件
##############################################################################################

import json
import math
import urllib
from bsddb import db
from utility.httputil import HttpUtility
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.basicinfostorage import BaseInfoStorage
from storage.commentsstorage import CommentsStorage
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from log.spiderlog import Logger
import traceback
import time
import datetime

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/11/18
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    COMMENTS_URL = 'http://hqcx.duoshuo.com/api/threads/listPosts.json?thread_key=%s&page=%d&order=desc'
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/18
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
        # @date：2016/11/18
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
        #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
        #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
        #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
        #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
        ##############################################################################################   

    def process(self, params):
        try:
            if params.step is AllComments.STEP_1:
                try:
                    threadid = self.r.parse('data-thread-key=\"(.*?)\"',params.content)[0];
                    comments_url = AllComments.COMMENTS_URL % (threadid, 1)
                    self.storeurl(comments_url, params.originalurl, AllComments.STEP_2, {'threadid':threadid,'pageno':1})  
                except:
                    return
            elif params.step is AllComments.STEP_2:
                try:
                    comments = json.loads(params.content)       
                    pagetotal= int(comments['cursor']['pages'])
                    comments_url = AllComments.COMMENTS_URL % (params.customized['threadid'],params.customized['pageno'])
                    self.storeurl(comments_url, params.originalurl, AllComments.STEP_3, 
                                  {'threadid':params.customized['threadid'], 
                                   'pageno':params.customized['pageno'],
                                   'totalpage':pagetotal})        
                except:
                    return
                                           
            elif params.step is AllComments.STEP_3:
                try:
                    if params.customized['pageno']<=params.customized['totalpage']:
                        comments = json.loads(params.content)
                        roll=len(comments['response'])
                        ptimer=[]
                        pcontent=[]
                        for key in comments['parentPosts'].keys():
                            ptime = comments['parentPosts'][key]['created_at']
                            ptime = ptime.split("+")[0]
                            ptime = ptime.replace("T"," ")
                            ptimer.append(datetime.datetime.strptime(ptime,'%Y-%m-%d %H:%M:%S'))
                            pcontent.append(comments['parentPosts'][key]['message'])
                        for ctime in range(0,len(ptimer)):
                            ptimer[ctime]=datetime.datetime.strptime(str(ptimer[ctime]),'%Y-%m-%d %H:%M:%S')
                        index=0
                        comments = []
                        complete = False
                        for comment in pcontent:
                            cmti = CommentInfo()
                            cmti.content = comment
                            if URLStorage.storeupdatetime(params.originalurl, str(ptimer[index])):
                                comments.append(cmti)
                            else:
                                complete = True
                                break;
                            index =index+ 1
                        self.commentstorage.store(params.originalurl, comments)
                        if not complete:
                                comments_url = AllComments.COMMENTS_URL % (params.customized['threadid'], params.customized['pageno']+1)
                                self.storeurl(comments_url, params.originalurl, AllComments.STEP_2, 
                                            {'threadid':params.customized['threadid'], 
                                            'pageno':params.customized['pageno']+1,
                                            'totalpage':params.customized['totalpage']})
                except:
                    return
        except Exception, e:
            traceback.print_exc()
            Logger.getlogging().error(e.message)