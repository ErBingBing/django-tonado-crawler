# coding=utf-8

#################################################################################
# @class：WangdafilmComments
# @author：JiangSiwei
# @date：2016/11/18
# @note：万达电影获取评论的文件，继承于WebSite类
#################################################################################

import json

from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo

class WangdafilmComments(SiteComments):
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 20
        self.pageno = 1

        self.COMMENTS_URL = 'http://www.wandafilm.com/wanda/news.do?m=getAllComment&pageNo={0}&displayCount={1}&newsId={2}'
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_NEXT_PAGE = 2 

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url,抽出的评论和最新评论的创建时间
    #          
    # @author：JiangSiwei
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到article_docid，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论信息， 
    #               并通过获取的hasnext的值是否为真，和last参数拼出下一个url,并传递给共通模块
    # @modified:Merlin.w.ouyang
    # @date：2016/12/12
    # @note:1、修正增量处理
    #       2、修正程序不能正常结束问题
    #       3、修正程序超时问题
    ##############################################################################################        
    #----------------------------------------------------------------------          
    def process(self, params):
        if params.step is self.STEP_DEFAULT_VALUE:
            self.step1(params)           
        elif params.step is self.STEP_COMMENT_FIRST_PAGE:
            self.step2(params) 
            
    #----------------------------------------------------------------------
    def  step1(self,params):
        try:
            newsId = self.r.parse('\d{3,}',params.url)[-1]
            comment_url = self.COMMENTS_URL.format(self.pageno,self.page_size,newsId)
            self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'newsId':newsId,'pageno':self.pageno})
        except:
            Logger.printexception()
            
    #----------------------------------------------------------------------    
    def step2(self,params):
        """获取评论的url"""
        try:
            newsId = params.customized['newsId']
            jsondata = json.loads(params.content)
            backflag=False
            if jsondata:
                comments = []
                for comment in jsondata:
                    cmti = CommentInfo()
                    if URLStorage.storeupdatetime(params.originalurl, str(comment['commentTime'])): 
                        cmti.content = comment['commentContent']
                        cmti.commentid = comment['commentId'] 
                        comments.append(cmti)
                    else: 
                        backflag=True
                self.commentstorage.store(params.originalurl, comments)  
                if backflag== False:
                    self.commentstorage.store(params.originalurl, comments)                  
                    self.pageno += 1
                    comment_url = self.COMMENTS_URL.format(self.pageno,self.page_size,newsId)
                    self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'newsId':newsId}) 
        except:
            Logger.printexception()
