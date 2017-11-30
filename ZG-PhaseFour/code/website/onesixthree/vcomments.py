# coding=utf-8

##############################################################################################
# @file：vcomments.py
# @author：Hedian
# @date：2016/12/05
# @version：Ver0.0.0.100
# @note：网易视频获取评论的文件
##############################################################r################################
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from log.spiderlog import Logger
import json
import math
import time


##############################################################################################
# @class：VComments
# @author：Hedian
# @date：2016/12/05
# @note：网易视频获取评论的类，继承于SiteComments类
##############################################################################################
class VComments(SiteComments):
    # COMMENT_FIRST_URL = 'http://comment.{channel}.163.com/{boardId}/{threadId}.html'
    #COMMENT_URL = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{threadId}/comments/newList?limit={limit}&offset={offset}'
    #PLAYCOUNT_URL = 'http://so.v.163.com/vote/{vid}.js'
    V_STEP_1 = None
    V_STEP_2 = 'V_STEP_2'
    V_STEP_3 = 'V_STEP_3'
    V_PLAYCOUNT = 'V_PLAYCOUNT'
    limit = 30
    get_threadId_url = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{threadId}'
    COMMENT_URL = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{threadId}/comments/newList?limit={limit}&offset={offset}'
    #limit = 20    

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/05
    # @note：VComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        
    def  process(self,params):
        """"""
        try:
            if params.step == VComments.V_STEP_1:
                self.step1(params)
            if params.step == VComments.V_STEP_2:
                self.step2(params)
            if params.step == VComments.V_STEP_3:
                self.step3(params)
        except:
            Logger.printexception()

    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        threadId = self.r.getid('docID', params.content,split=':')
        if not threadId:
            threadId = self.r.getid('threadId', params.content)
        if not threadId:
            Logger.getlogging().warning('{}:40000 No threadId'.format(params.originalurl))
            return
            
        commentinfo_url = VComments.get_threadId_url.format(threadId=threadId)
        self.storeurl(commentinfo_url, params.originalurl, VComments.V_STEP_2, {'threadId':threadId})
    
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        try:
            threadId = params.customized['threadId']
            jsondata  = json.loads(params.content)
            comment_totalnum = jsondata['tcount']
            NewsStorage.setcmtnum(params.originalurl, comment_totalnum)
        except:
            Logger.getlogging().warning('{}:30000 No comments'.format(params.originalurl))
            return            
        #更新数据库
            cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= int(comment_totalnum):
            return

            max = int(math.ceil(float(comment_totalnum  - cmtnum)/VComments.limit))
        if max > self.maxpages:
            max = self.maxpages
        #if offsets == 1:
            #self.step3(params)
        for offset in range(1, max + 1, 1):
            if page == 1:
                self.step3(params)
                continue
            comment_url = VComments.COMMENT_URL.format(threadId=threadId,
                                                       limit=VComments.limit,
                                                       offset=offset*VComments.limit)
            self.storeurl(comment_url, params.originalurl, VComments.V_STEP_3, {'threadId':threadId})
        
    #----------------------------------------------------------------------
    def step3(self,params):
        """"""
        try:
            jsondata  = json.loads(params.content)
            comments = jsondata['comments']         
        except:
            Logger.getlogging().warning('{}:30000 No comments'.format(params.originalurl))
            return
        
        cmts = []
        for key in comments:
            try:
                nickname = comments[key]['user']['nickname']
            except:
                nickname = 'anonymous'
            # 得到标准日期格式
            curtime = TimeUtility.getuniformtime(str(comments[key]['createTime']))
            content = comments[key]['content']
            if not CMTStorage.exist(params.originalurl, content, curtime, nickname):
                CMTStorage.storecmt(params.originalurl, content, curtime, nickname)
