# coding=utf-8
##############################################################################################
# @file：bilibilicomments.py
# @author：Han Luyang
# @date：2017/09/11
# @note：bilibili视频网站获取评论的文件
##############################################################################################
import json
import time
import re
import math
import random
from bs4 import BeautifulSoup as bs
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import getuniformtime
from log.spiderlog import Logger
from configuration import constant 
##############################################################################################
# @class：BilibiliComments
# @author：Han Luyang
# @date：2017/09/11
# @note：bilibili视频网站获取评论的类，继承于SiteComments类
##############################################################################################
class BilibiliComments(SiteComments):
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：BilibiliComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.pageUrl = 'http://api.bilibili.com/x/v2/reply?pn={page}&type=1&oid={videoId}&sort=0'
        self.playurl = 'https://interface.bilibili.com/player?id=cid:{cid}&aid={aid}'
        self.pageSize = 20.0
        self.STEP_COUNT = None
        self.STEP_PAGES = 1
        self.STEP_CMTS = 2
        self.STEP_PLAY = 'play'

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的分页url
    #          Step2：获取评论信息
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：step0: 由于评论动态加载，basicinfo无法解析评论数；该步骤将原始url转化为实际请求的url，并向共通模块传递参数
    #        step1：通过共通模块传入的html内容获取到page和videoId，拼出分页url，并传递给共通模块
    #        step2：通过共通模块传入的html内容获取到评论信息
    ##############################################################################################
    def process(self, params):
        try:
            if params.step == self.STEP_COUNT:
                self.step0(params)
            elif params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_CMTS:
                self.step2(params)
            elif params.step == self.STEP_PLAY:
                self.getclick(params)
        except:
            Logger.printexception()
    
    ##############################################################################################
    # @functions：step0
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：由于评论动态加载，basicinfo无法解析评论数；该步骤将原始url转化为实际请求的url，并向共通模块传递参数
    ##############################################################################################        
    def step0(self, params):
        try:
            url = params.originalurl
            #！！！！！！！ 不匹配的情况   data-aid
            pattern = '^https?://www.bilibili.com/video/av(\d+)/?'
            if not self.r.search(pattern, url):
                Logger.log(url, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
                return 
            videoId = self.r.parse(pattern, url)[0] 
            baseUrl = self.pageUrl.format(page = 1, videoId = videoId)
            self.storeurl(baseUrl, url, self.STEP_PAGES,  {'videoId':videoId})
            cid = self.r.getid('cid', params.content, split='=')
            aid = videoId
            if not cid:
                cid = str(random.randint(10**7,10**8-1))
                playurl = self.playurl.format(cid=cid, aid=aid)     
                self.storeurl(playurl, url, self.STEP_PLAY, {'videoId':videoId})
            else:
                Logger.log(url, constant.ERRORCODE_SITE_NOGET_CLICKNUM)
        except:
            Logger.printexception()
    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：None
    # @author：Han Luyang
    # @date：2017/09/11
    # @note：传递分页url给共通模块
    
    #prevCmtsCount < currCmtsCount 有三种情况。1. 一级评论数量有更新；2. 二级评论数量有更新；3. 一二级评论数量均有更新；
    # 一旦出现二级评论数量有更新的情况，遍历所有评论页并基于时间比较的方法是最好的（综合考虑考虑逻辑简单性和有效性）；
    # 原因是：1. 更新的二级评论可能会出现在较老的一级评论下（比如，较老的hot评论），这使得希望减少遍历的方法变得无效；
    # 2. 在某次更新时，如果因为某种异常导致某些评论存入失败，那么自此以后的每次评论数量比较，都会有不可弥补的差别，这使得基于
    # 数目比较的方法变得无效。综上，这里选择简单直接的遍历及时间比较。        
    # 评论总页数, 这里hasCmts是一级评论数（分页是按一级评论来的）    
    ##############################################################################################    
    def step1(self, params):
        try: 
            url = params.originalurl
            videoId = params.customized['videoId']
            params.content = params.content[params.content.index('{'):params.content.rindex('}')+1]
            jsonData = json.loads(params.content)['data']
            hasCmts = jsonData['page']['count']
            # 是否有评论
            if not hasCmts:
                return
            # 比较增量：获取现在评论数目及上次采集的评论数目
            currCmtsCount = jsonData['page']['acount']
            NewsStorage.setcmtnum(url, currCmtsCount)
            prevCmtsCount = int(CMTStorage.getcount(url))
            # 若没有评论更新，跳过
            if prevCmtsCount >= currCmtsCount:
                return
            # 更新评论数
            pageNum = int(math.ceil((hasCmts-prevCmtsCount)/self.pageSize))
            # 上次采集数据的截止时间         
            # 生成分页url并传递给共通模块
            for page in range(1, pageNum + 1):
                if page == 1:
                    self.step2(params)
                pageUrl = self.pageUrl.format(page = page, videoId = videoId)
                self.storeurl(pageUrl, url, self.STEP_CMTS)
        except:
            Logger.printexception()
            
    def step2(self, params):     
        # 获取replies
        jsonReplies = json.loads(params.content)['data']['replies']
        for cmt in jsonReplies:
            try:
                cmtContent = cmt['content']['message']
                cmtPubDate = cmt['ctime']
                cmtUser = ''
                # 存储评论
                CMTStorage.storecmt(params.originalurl, cmtContent, cmtPubDate, cmtUser)
            except:
                Logger.printexception()
    #----------------------------------------------------------------------
    def getclick(self, params):
        print params.content.replace('\n', ' ').replace('\r', '')
        pattern1 = '<click>(\d+)</click>'
        pattern2 = '&lt;click&gt;(\d+)&lt;/click&gt;'
        if self.r.search(pattern1, params.content):
            click = self.r.parse(pattern1, params.content)[0]
            NewsStorage.setclicknum(params.originalurl, int(click))
        elif self.r.search(pattern2, params.content):
            click = self.r.parse(pattern2, params.content)[0]
            NewsStorage.setclicknum(params.originalurl, int(click))     
        else:
            Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)