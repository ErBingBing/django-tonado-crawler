# -*- coding: utf-8 -*-
##############################################################################################
# @file：baozoucomments.py
# @author：Han Luyang
# @date：2017/09/11
# @note：暴走漫画获取评论的文件
###############################################################################################
import re
import json
import time
import math
from bs4 import BeautifulSoup as bs

from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import getuniformtime
from log.spiderlog import Logger

##############################################################################################
# @class：BaozouComments
# @author：Han Luyang--》yongjicao
# @date：2017/09/11---》2017/09/26
# @note：暴走漫画获取评论的类，继承于SiteComments类
##############################################################################################
class BaozouComments(SiteComments):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：初始化配置
    COMMENT_URL = 'http://baozou.com/api/v2/articles/{topic_id}/web_comments?page={page}&per_page={per_page}'
    URL_INFO_URL = 'http://baozou.com/scores?{topic_id}'
    STEP_PAGES = None
    STEP_2= '2'
    STEP_3= '3'
    STEP_4= '4'
    PER_PAGE = 100
    ################################################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        # # 注意，不管是video还是article的评论格式都是api/v2/articles
        # COMMENT_URL = 'http://baozou.com/api/v2/articles/{topic_id}/web_comments?page={page}'
        # self.childCmtsPageUrl = 'http://baozou.com/api/v2/comments/{cmtId}/children_comments?page={page}'
        # self.cmtsPageSize = 10.0
        # self.childCmtsPageSize = 5.0
        # self.STEP_PAGES = None
        # self.STEP_CMTS = 1
        # self.STEP_CHILD_CMTS = 2

    ################################################################################################################
    # @functions：process
    # @params：共通模块参数url，原始url，step及自定义参数
    # @return：none
    # @author: Han Luyang
    # @date: 2017/09/11
    # @note：step1. 解析url，产生评论分页url，并向共通模块传递
    #        step2. 解析分页url，存储一级评论信息；产生二级评论分页url，并向共通模块传递
    #        step3. 解析分页url，存储二级评论信息
    ################################################################################################################
    def process(self, params):
        try:
            if params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_2:
                self.step2(params)
            elif params.step == self.STEP_3:
                self.step3(params)
            elif params.step == self.STEP_4:
                self.setplayinfo(params)
        except:
            Logger.printexception()
    
    ##############################################################################################
    # @functions：step1
    # @param: 共通模块参数url，原始url，step及自定义参数
    # @return: None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析url，产生评论分页url，并向共通模块传递
    ###############################################################################################    
    def step1(self, params):
        topic_id = self.r.parse('^http://baozou.com/\w+/(\d+).*', params.originalurl)[0]
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = BaozouComments.COMMENT_URL.format(topic_id=topic_id, page=1,per_page = self.PER_PAGE)
        self.storeurl(commentinfo_url, params.originalurl, BaozouComments.STEP_2, {'topic_id': topic_id})
        playinfo_url = BaozouComments.URL_INFO_URL.format(topic_id=topic_id)
        self.storeurl(playinfo_url, params.originalurl, BaozouComments.STEP_4, {'topic_id': topic_id})
        #######################################################################################################
        # url = params.originalurl
        # soup = bs(params.content, 'html5lib')
        # # 是否有评论
        # hasCmts = soup.select('.count')
        # if not hasCmts:
        #     return
        # # 现在评论数及上次评论数
        # currCmtsCount = int(hasCmts[0].string.strip())
        # prevCmtsCount = CMTStorage.getcount(url)
        #
        # if prevCmtsCount >= currCmtsCount:
        #     return
        # NewsStorage.setcmtnum(url, currCmtsCount)
        #
        # artId = self._getArtId(url)
        # # 是否分页
        # multiPages = soup.find_all(class_='page-link')
        # if not multiPages:
        #     pageNum = 1
        # else:
        #     pageNum = int(multiPages[-2].string.strip())
        # # 上次评论截止时间
        # lastPubTime = CMTStorage.getlastpublish(url)
        # lastTimestamp = int(time.mktime(time.strptime(lastPubTime, '%Y-%m-%d %H:%M:%S')))
        # # 拼接分页url，并传递给共通模块
        # for page in range(1, pageNum + 1):
        #     pageUrl = self.cmtsPageUrl.format(artId = artId, page = page)
        #     self.storeurl(pageUrl, url, self.STEP_CMTS, others = {'lastTs':lastTimestamp})
            
    ##############################################################################################
    # @functions：step2
    # @param: 共通模块参数url，原始url，step及自定义参数
    # @return: None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析分页url，存储一级评论信息；产生二级评论分页url，并向共通模块传递
    ###############################################################################################
    def step2(self, params):
        topic_id = params.customized['topic_id']
        commentsinfo = json.loads(params.content)
        comments_count = commentsinfo['total_count']
        # pagenum = commentsinfo['total_pages']
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        # 保存页面评论量
        cmtnum = CMTStorage.getcount(params.originalurl)
        if cmtnum >= comments_count:
            return
        pagenum = int(math.ceil(float(comments_count - cmtnum) / self.PER_PAGE))
        if pagenum >= self.maxpages:
            pagenum = self.maxpages
        for index in range(1, pagenum + 1, 1):
            if index == 1:
               self.step3(params)
               continue
            commentinfo_url = BaozouComments.COMMENT_URL.format(topic_id=topic_id, page=index,per_page = self.PER_PAGE)
            self.storeurl(commentinfo_url, params.originalurl, BaozouComments.STEP_3)
        #############################################################################################################
        # try:
        #     url = params.originalurl
        #     jsonCmts = json.loads(params.content)['comments']
        #     lastTimestamp = params.customized['lastTs']
        #     # 存储一级评论
        #     self._storeCmt(url, jsonCmts, lastTimestamp)
        #     # 产生二级评论分页url，并向共通模块传递
        #     for cmt in jsonCmts:
        #         childCmtsCount = cmt['children_count']
        #         if not childCmtsCount:
        #             continue
        #
        #         cmtId = cmt['id']
        #         pageNum = int(math.ceil(childCmtsCount/self.childCmtsPageSize))
        #         for page in range(1, pageNum + 1):
        #             pageUrl = self.childCmtsPageUrl.format(cmtId = cmtId, page = page)
        #             self.storeurl(pageUrl, url, self.STEP_CHILD_CMTS, others = {'lastTs':lastTimestamp})
        # except:
        #     Logger.printexception()

    ##############################################################################################
    # @functions：step3
    # @param: 共通模块参数url，原始url，step及自定义参数
    # @return: None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析分页url，存储二级评论信息
    ###############################################################################################    
    def step3(self, params):
        #####################################################################################
        # try:
        #     url = params.originalurl
        #     jsonCmts = json.loads(params.content)['children_comments']
        #     lastTimestamp = params.customized['lastTs']
        #     # 存储二级评论
        #     self._storeCmt(url, jsonCmts, lastTimestamp)
        # except:
        #     Logger.printexception()
        #####################################################################################
        commentsinfo = json.loads(params.content)
        for index in range(0, int(len(commentsinfo['comments'])), 1):
            content = commentsinfo['comments'][index]['content']
            curtime = commentsinfo['comments'][index]['created_at']
            if not CMTStorage.exist(params.originalurl, content, curtime, ''):
                 CMTStorage.storecmt(params.originalurl, content, curtime, '')

    ##############################################################################################
    # @functions：_storeCmt
    # @param: 主体url，评论列表，上次评论的截至时间戳
    # @return: None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：存储评论模块，供step2及step3调用
    ###############################################################################################            
    # def _storeCmt(self, url, cmts, lastTs):
    #     jsonCmts = cmts
    #     lastTimestamp = lastTs
    #     for cmt in jsonCmts:
    #         cmtPubTime = cmt['created_at']
    #         cmtTimestamp = int(time.mktime(time.strptime(cmtPubTime, '%Y-%m-%d %H:%M:%S')))
    #         if cmtTimestamp < lastTimestamp:
    #             break
    #
    #         cmtContent = cmt['content']
    #         cmtUser = ''
    #         CMTStorage.storecmt(url, cmtContent, cmtPubTime, cmtUser)
    #
    ##############################################################################################
    # @functions：_getArtId
    # @param: url
    # @return: None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：解析出artId
    ###############################################################################################    
    # def _getArtId(self, url):
    #     patt = '^http://baozou\.com/(?:videos|articles)/(\d+)\S*'
    #     ret = re.findall(patt, url)[0]
    #     return ret
    ##############################################################################################
    # @functions：setplayinfo
    # @param: url
    # @return: None
    # @author：yongjicao
    # @date：2017/09/26
    # @note：获取votenum
    def setplayinfo(self,params):
        try:
            topic_id = params.customized['topic_id']
            jsondata = json.loads(params.content)
            votenum = jsondata[topic_id]['pos']
            NewsStorage.setvotenum(params.originalurl,votenum)
        except:
            Logger.getlogging().debug(params.originalurl)

        
            
            
        

