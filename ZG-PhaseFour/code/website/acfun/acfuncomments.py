# coding=utf-8
##############################################################################################
# @file：acfuncomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：AcFun评论获取
# @modify
# @author:Jiangsiwei
# @date:2017/01/12
# @note:网站域名更新升级，原地址：http://www.acfun.tv/ 升级后地址：http://www.acfun.cn/
#      取评论逻辑没变
##############################################################################################

import json
import re
from website.common.comments import SiteComments
from log.spiderlog import Logger
import traceback
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from dao.sqldao import SQLDAO
from configuration import constant 
##############################################################################################
# @class：AcfunComments
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AcfunComments(SiteComments):
    COMMENTS_URL = 'http://www.acfun.cn/comment_list_json.aspx?isNeedAllCount=true&contentId=%d&currentPage=1&pageSize=%d'

    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_CLICK = 4
    INFO_URL = 'http://www.acfun.cn/content_view.aspx?contentId={con_id}'


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/20
    # @note：AcfunComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

        #----------------------------------------------------------------------
        ##############################################################################################
        # @functions：process
        # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
        # @return：Step1：获取评论的首页url
        #          Step2：获取评论的所有url
        #          Step3: 抽出的评论和最新评论的创建时间
        # @author：Merlin.W.ouyang
        # @date：2016/11/20
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：获取所有评论的那个URL页面
        #        Step3：由于评论不是按照时间排序，所以都取出来进行实践排序，通过实践判断获取增量评论
        ##############################################################################################   
        
    def process(self, params):
        try:
            if params.step is AcfunComments.STEP_1:
                self.step1(params)
                self.get_clickurl(params)
            elif params.step is AcfunComments.STEP_2:
                self.step2(params)
            elif params.step is AcfunComments.STEP_3:
                self.step3(params)
            elif params.step is AcfunComments.STEP_CLICK:
                self.setclick(params)
        except:
            Logger.printexception()
    ####################################################################################################################

    def step1(self,params):
        key = int(re.findall("\d+", params.url.split("/")[-1])[0])
        comments_url = AcfunComments.COMMENTS_URL % (key, 1)
        self.storeurl(comments_url, params.originalurl, AcfunComments.STEP_2,
                      {'key': key,
                       'commentcount': 0})

    def step2(self,params):
        comments = json.loads(params.content)
        commentcount = int(comments['data']['totalCount'])
        NewsStorage.setcmtnum(params.originalurl, commentcount)
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= commentcount:
            return
        comments_url = AcfunComments.COMMENTS_URL % (params.customized['key'], commentcount)
        self.storeurl(comments_url, params.originalurl, AcfunComments.STEP_3,
                      {'key': params.customized['key'],
                       'commentcount': commentcount})

    def step3(self,params):
        comments = json.loads(params.content)
        for id in comments['data']['commentContentArr']:
            content = comments['data']['commentContentArr'][id]['content']
            pubtime = comments['data']['commentContentArr'][id]['postDate']
            nick = comments['data']['commentContentArr'][id]['userName']
            CMTStorage.storecmt(params.originalurl, content, pubtime , nick)
            
    ####################################################################################################################
    def get_clickurl(self, params):
        originalurl = params.originalurl
        con_id = originalurl.split('/')[-1].split('ac')[-1]
        clickurl = AcfunComments.INFO_URL.format(con_id=con_id)
        self.storeurl(clickurl, params.originalurl, AcfunComments.STEP_CLICK)

    def setclick(self, params):
        try:
            content = json.loads(params.content)
            # content=[播放量，评论，X，X,弹幕,收藏数，投焦数，X]
            cmtnum = content[1]
            clicknum = content[0]
            votenum = content[-2]
            fansnum =content[-3]
            if not cmtnum:
                cmtnum = 0
            if not clicknum:
                clicknum = 0
            if not votenum:
                votenum = 0
            if not fansnum:
                fansnum = 0
            NewsStorage.seturlinfo(params.originalurl, 
                                   data={SQLDAO.SPIDER_TABLE_NEWS_CMTNUM:   cmtnum,
                                         SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM: clicknum,
                                         SQLDAO.SPIDER_TABLE_NEWS_VOTENUM:  votenum,
                                         SQLDAO.SPIDER_TABLE_NEWS_FANSNUM:  fansnum})

        except:
            Logger.printexception()
