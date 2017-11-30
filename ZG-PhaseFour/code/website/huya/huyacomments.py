# coding=utf-8

##############################################################################################
# @file：huyacomment.py
# @author：Hedian
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：多玩视频获取评论的文件
##############################################################r################################

import json
import math
import datetime
import time
from lxml import etree

from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from storage.urlsstorage import URLCommentInfo
from utility.common import Common
from log.spiderlog import Logger
from utility.timeutility import TimeUtility

##############################################################################################
# @class：HuyaComments
# @author：Hedian
# @date：2016/11/20
# @note：多玩视频获取评论的类，继承于SiteComments类
##############################################################################################
class HuyaComments(SiteComments):
    #COMMENTS_URL = 'http://comment3.duowan.com/index.php?r=comment/comment&order=time&noimg=true&uniqid={uniqid}&domain={domain}&url={url}&num={num}'
    COMMENTSTOTAL_URL= 'http://v-comments.huya.com/index.php?r=comment/totaljson&&uniqid={uniqid}&domain={domain}&url={url}'
    COMMENTS_URL = 'http://v-comments.huya.com/index.php?r=comment/comment&order=hot&noimg=true&uniqid={uniqid}&domain={domain}&url={url}&huya={page}'
    DEFAULT_PAGE_SIZE = 10 #无法通过设置pagesize来调整获每次获取的评论数，只能10个为单位获取
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/20
    # @note：HuyaComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：HuyaComments的入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is HuyaComments.STEP_1:
                self.step1(params)
            elif params.step == HuyaComments.STEP_2:
                self.step2(params)
            elif params.step == HuyaComments.STEP_3:
                self.step3(params)    
        except:
            Logger.printexception()


    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入url，拼出获取所有评论的url
    ##############################################################################################
    def step1(self, params):
        #1. 下载html，使用正则表达式获取下面值
        Logger.getlogging().debug(params.originalurl)
        uniqid = self.r.getid('comment3Uniqid', params.content,'=')
        domain = self.r.parse('http[s]{0,1}://(.*\.com).*',params.url)[0]
        url = self.r.parse('http[s]{0,1}://.*\.com(.*\.html)',params.url)[0]
        commentstotal_url = HuyaComments.COMMENTSTOTAL_URL.format(uniqid=uniqid, domain=domain, url=url)
        self.storeurl(commentstotal_url, params.originalurl, HuyaComments.STEP_2,{'uniqid':uniqid, 'domain':domain, 'url':url})        
     
    #----------------------------------------------------------------------
    def  step2(self,params):
        """"""
        uniqid = params.customized['uniqid']
        domain = params.customized['domain']
        url = params.customized['url']
        jsondata = json.loads(params.content)
        comments_count = int(jsondata['show']['total_num'])
        # 检查评论数是否增加，没有增加，返回；有增加，更新增加后的页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= int(comments_count):
            return
        URLStorage.setcmtnum(params.originalurl, int(comments_count))

        #3. 拼出获取所有评论的url
        max = int(math.ceil(float(comments_count) / HuyaComments.DEFAULT_PAGE_SIZE))
        for page in range(1, max + 1, 1):
            #num = (page - 1)*HuyaComments.DEFAULT_PAGE_SIZE
            comments_url = HuyaComments.COMMENTS_URL.format(uniqid=uniqid, domain=domain, url=url, page=page)
            self.storeurl(comments_url, params.originalurl, HuyaComments.STEP_3)


    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        jsondata = json.loads(params.content)
        comments = []
        for comment in jsondata:
            cmti = CommentInfo()
            curcomtime = int(comment['created'])

            # 检查是否需要更新当前抓取的评论的最新时间，第一条评论时间就是最新评论时间
            if URLStorage.storeupdatetime(params.originalurl, TimeUtility.getuniformdate2(curcomtime)):
                cmti.content = comment['contents']
                comments.append(cmti)

                # 检查是否有评论回复
                if int(comment['comment_reply_total']) > 0:
                    reply = comment['reply']
                    # 获取所有的评论回复
                    for num in range(0, int(comment['comment_reply_total']), 1):
                        recmti = CommentInfo()
                        recmti.content = reply[num]['contents']
                        comments.append(recmti)
        if len(comments) >= 0:
        # 保存获取的评论
            self.commentstorage.store(params.originalurl, comments)
