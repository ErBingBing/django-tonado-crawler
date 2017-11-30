# encoding=utf-8

#################################################################################
# @TianyaComments
# @author：JiangSiwei
# @date：2016/11/28
# @note：天涯获取论坛评论的文件，继承于SiteComments类
# @modify
# @author:Jiangsiwei
# @date:2017/01/13
# @note:122-123代码提取时间有误，跟新代码后ok
#################################################################################

import json
import math
import time
from utility.gettimeutil import getuniformtime
from bs4 import BeautifulSoup
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
import traceback


class TianyaComments(SiteComments):
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 10
        self.COMMENTS_SOURCE_URL = 'http://bbs.tianya.cn/post-{item}-{artId}-{page}.shtml'        #'format(merNum=merNum,page=pageCount)'
        self.COMMENTS_CHILD_URL = 'http://bbs.tianya.cn/api?method=bbs.api.getCommentList&params.item={item}&params.articleId={artId}&params.replyId={replyId}&params.pageNum={page}'
                            #'format(merNum=merNum,replyId=replyId,page=pageNum)
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_CHILD_PAGE = 2

        self.ITEM_FORMAT = 'ext2\s*:\s*\"(.+?)\"'
        self.ARTID_FORMAT = 'ext1\s*:\s*\"(.+?)\"'

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url,抽出的评论和最新评论的创建时间
    #          
    # @author：JiangSiwei
    # @date：2016/11/28
    # @note：Step1：先通过originalurl获取到能获取comment_id的url,并传递给共通模块，通过获取html中得到comment_id及url_id 
    #        Step2：通过共通模块传入的html内容获取到评论总数及item,artId，拼出获取评论的url，并传递给共通模块
    #               通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则保存最新更新时间 
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则抓取新增的数据
    #               
    ##############################################################################################        
    #----------------------------------------------------------------------          
    def process(self, params):
        """
        """ 
        if params.step == self.STEP_DEFAULT_VALUE:
            self.step1(params)
        elif params.step == self.STEP_COMMENT_FIRST_PAGE:
            self.step2(params)
        elif params.step == self.STEP_COMMENT_CHILD_PAGE:
            self.step3(params)            
        
    ################################################################################################################
    # @functions：step1
    # @params： params
    # @return：none
    # @note：获取url_id关键字
    ################################################################################################################            
    #----------------------------------------------------------------------    
    def step1(self,params):
        """获取评论的首页url,并在首页中提取主贴正文及相关字段"""
        try:
            if not self.r.search(self.ITEM_FORMAT,params.content):
                return
            if not self.r.search(self.ARTID_FORMAT,params.content):
                return
            item = self.r.parse(self.ITEM_FORMAT,params.content)[0]
            artId = self.r.parse(self.ARTID_FORMAT,params.content)[0]
            soup = BeautifulSoup(params.content,'html5lib')

            if soup.select('#container > .wd-question'):
                # 通过评论时间来判断增量
                self.getanswers(params)
                return
            alt_items = soup.select('.atl-main > .atl-item')
            #主贴内容、时间、评论数
            main_content = alt_items[0].select_one('.bbs-content').get_text()
            comments_count = self.r.parse('\d+',soup.select('.atl-info')[0].get_text())[-1]

            # 通过评论数量判断增量
            cmtnum = CMTStorage.getcount(params.originalurl,True)
            if cmtnum >= comments_count:
                return

            NewsStorage.setcmtnum(params.originalurl, comments_count)
            pageCount = self.r.parse('pageCount\s:\s(\d+?),',params.content)[0]
            for page in range(1,int(pageCount)+1):
                if page == 1:
                    params.customized['item'] = item
                    params.customized['artId'] = artId
                    params.customized['page'] = page
                    self.step2(params)
                    continue
                comment_source_url = self.COMMENTS_SOURCE_URL.format(item=item,artId=artId,page=page)  
                self.storeurl(comment_source_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'item':item,'artId':artId,'page':page})
        except:
            Logger.printexception()
            
    ################################################################################################################
    # @functions：step2
    # @params： params
    # @return：none
    # @note：获取评论的评论url
    ################################################################################################################               
    #----------------------------------------------------------------------
    def  step2(self,params):
        """获取评论,和评论的评论url"""
        item = params.customized['item']
        artId = params.customized['artId']
        page = params.customized['page']

        #step1.先定位到atl-main/atl-item,取其中的主评论正文,时间,replyid,子评论数
        #step2.通过 子评论数/10 获取自评论页数pageNum
        #step3.通过 merNum,rellyid,pageNum拼出子评论id
    
        soup = BeautifulSoup(params.content,'html5lib')
        alt_items = soup.select('.atl-main > .atl-item')       
        #print 'alt_items:',len(alt_items)
        
        if page == 1:
            alt_items =alt_items[1:]
 
        for alt_item in alt_items:
            curtime = alt_item.select('.atl-head > div.atl-info > span')
            curtime = getuniformtime(curtime[-1].get_text())

            main_comment = alt_item.select_one('.bbs-content').get_text()
            replyid = alt_item.select_one('a[class="reportme a-link"]').get('replyid')
            

            content = main_comment.strip()
            commentid = replyid
            nick = alt_item.select_one('a[class="js-vip-check"]').get_text()
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

            child_comment_num = alt_item.select_one('a[class="a-link-2 ir-remark"]').get_text()
            if self.r.search('\d+',child_comment_num):
                child_comment_num = self.r.parse('\d+',child_comment_num)[0]
            else:
                child_comment_num = 0
                continue
            pageNum = int(math.ceil(float(child_comment_num)/ self.page_size))
            for page in range(1,int(pageNum)+1):
                child_url = self.COMMENTS_CHILD_URL.format(item=item,artId=artId,replyId=replyid,page=page)
                #print 'child_url:',child_url
                self.storeurl(child_url, params.originalurl, self.STEP_COMMENT_CHILD_PAGE,{'item':item,'artId':artId})           
    ################################################################################################################
    # @functions：step3
    # @params： params
    # @return：none
    # @note：获取json文件中的评论和相关数据
    ################################################################################################################                    
    #----------------------------------------------------------------------
    def step3(self,params):
        jsondata = json.loads(params.content)
        for comment in jsondata['data']:

            content = comment['content']
            commentid = comment['id']
            curtime = getuniformtime(comment['comment_time'])
            nick = "none"
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

            
    #----------------------------------------------------------------------
    def getanswers(self,params):
        """"""
        soup = BeautifulSoup(params.content,'html5lib')
        answers = soup.select('.answer-wrapper > .answer-item')
        # comments = []
        for answer in answers:
            tm = answer.select_one('.user').get_text()
            curtime = getuniformtime(tm)
            # lasttime = CMTStorage.getlastpublish(params.originalurl,True)
            # 通过评论最新时间来判断增量
            # if curtime > lasttime:
            content = answer.select_one('.content').get_text()
            nick = "none"
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)


            
            
        