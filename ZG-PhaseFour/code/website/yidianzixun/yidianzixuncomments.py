# coding=utf8

#################################################################################
# @class：YidianzixunComments
# @author：JiangSiwei
# @date：2016/11/18
# @note：搜狐获取评论的文件，继承于WebSite类
#################################################################################

import json

from log.spiderlog import Logger
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage


class YidianzixunComments(SiteComments):
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 30

        # self.COMMENTS_SOURCE_URL = 'http://www.yidianzixun.com/api/q/?path=contents/comments&version={0}&docid={1}&count={2}'
        # self.COMMENTS_URL = 'http://www.yidianzixun.com/api/q/?path=contents/comments&version={0}&docid={1}&last_comment_id={3}&count={2}'
        self.COMMENTS_URL = 'http://www.yidianzixun.com/home/q/getcomments?docid={0}&count={1}&last_comment_id={2}&appid=web_yidian'
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_NEXT_PAGE = 2

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url,抽出的评论和最新评论的创建时间
    #          
    # @author：QW_Liang
    # @date：2017/9/18
    # @note：Step1：通过共通模块传入的html内容获取到article_docid，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论信息， 并获取最后一个cmti.commentid拼出下一个url,并传递给共通模块
    ##############################################################################################
    def process(self, params):
        if params.step == self.STEP_DEFAULT_VALUE:
            self.step1(params)
        elif params.step == self.STEP_COMMENT_FIRST_PAGE:
            self.step2(params)

    def step1(self, params):
        """获取评论的首页url"""
        try:
            if self.r.search('^http[s]{0,1}://.*\.yidianzixun\.com/article/\w+',params.originalurl):
                docid = self.r.parse('^http[s]{0,1}://.*\.yidianzixun\.com/article/(\w+)', params.originalurl)[0]
            comment_source_url = self.COMMENTS_URL.format(docid,self.page_size,'')
            # article_docid = self.r.parse('yidian.article_docid = \"(\w+)\"', params.content)[0]
            # comment_source_url = self.COMMENTS_SOURCE_URL.format('999999', article_docid, self.page_size)
            self.storeurl(comment_source_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,
                          {'docid': docid})
        except:
            Logger.printexception()

    def step2(self, params):
        """获取评论及下一个url"""
        try:
            jsondata = json.loads(params.content)
            total = jsondata['total']
            NewsStorage.setcmtnum(params.originalurl, total)
            if total == 0:
                return
            cmtnum = CMTStorage.getcount(params.originalurl, True)
            if cmtnum >= total:
                return
        except:
            Logger.printexception()
        self.getcomments(params)

    def getcomments(self,params):
        docid = params.customized['docid']
        jsondata = json.loads(params.content)
        if len(jsondata['comments'])>0:
            index = 0
            for comment in jsondata['comments']:
                commentid = comment['comment_id']
                content = comment['comment']
                curtime = comment['createAt']
                nick = comment['nickname']
                if index == len(jsondata['comments'])-1:
                    last_comment_id = commentid
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                index +=1
            comment_source_url = self.COMMENTS_URL.format(docid, self.page_size, last_comment_id)
            self.storeurl(comment_source_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,
                          {'docid': docid,'last_comment_id':last_comment_id})
        else:
            return
