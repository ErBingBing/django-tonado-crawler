# encoding=utf8

#################################################################################
# @class：SyqnrComments
# @author：QW_Liang
# @date：2017/9/15
# @note:手游圈内人获取评论的文件，继承于SiteComments类
#################################################################################

import json
import math

from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger


class SyqnrComments(SiteComments):
    
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 5
        self.COMMENTS_URL = 'http://www.syqnr.com/api/?action=com&do=comment&sid={0}&cid={1}&start={2}&length={3}'
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_NEXT_PAGE = 2          
      
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/9/15
    # @note：Step1：通过共通模块传入的html内容获取到cid,sid，拼出获取评论首页的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块    
    ##############################################################################################        
    #----------------------------------------------------------------------          
    def process(self, params):
        """""" 
        if params.step == self.STEP_DEFAULT_VALUE:
            self.step1(params)
        elif params.step == self.STEP_COMMENT_FIRST_PAGE:
            self.step2(params)
        elif params.step == self.STEP_COMMENT_NEXT_PAGE:
            self.step3(params)  
            
    #----------------------------------------------------------------------
    def step1(self, params):
        """获取评论的首页url"""
        try:
            cid,sid = self.r.parse('\"contentid\":\"(\d+?)\".*\"sid\":(\d+?)',params.content)[0]
            
            comment_url=self.COMMENTS_URL.format(sid,cid,0,self.page_size)
            self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'cid':cid,'sid':sid}) 
        except:
            Logger.getlogging().error('{0}:30000'.format(params.originalurl))
            Logger.printexception()
            
    #----------------------------------------------------------------------
    def  step2(self,params):
        """获取评论的其他url"""
        try:
            sid = params.customized['sid']
            cid = params.customized['cid']
            try:
                comments = json.loads(params.content)
                comments_count = float(comments['total'])
            except:
                Logger.getlogging().error('{0}:30000'.format(params.originalurl))
                Logger.printexception()  
                return
            #根据cmtnum判断是否有增量
            cmtnum = CMTStorage.getcount(params.originalurl,True)
            if cmtnum >= comments_count:
                return
            NewsStorage.setcmtnum(params.originalurl, comments_count)

            if int(comments_count) == 0:
                Logger.getlogging().info('comments count:{count}'.format(count = comments_count))            
                return

            # 最多只取十页评论
            page_num = int(math.ceil(float(comments_count - cmtnum) / self.page_size))
            if page_num >= self.maxpages:
                page_num = self.maxpages
            # page_num=int(math.ceil((comments_count/self.page_size)))
            for page in range(0,page_num):
                url=self.COMMENTS_URL.format(sid,cid,page,self.page_size)
                self.storeurl(url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE,{'cid':cid,'sid':sid})


        except:
            Logger.printexception()
        
        
    #----------------------------------------------------------------------
    def  step3(self,params):
        """通过评论的url获取评论"""
        try:
            jsondata = json.loads(params.content)

            for comment in jsondata['data']:

                content = comment['content']
                commentid = comment['id']
                #保存评论时间
                pubtime = comment['datetime']
                #获取评论时间
                curtime = TimeUtility.getuniformtime(pubtime)

                nick = -1
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()
               
 
              
        

