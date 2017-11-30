# coding=utf-8

##############################################################################################
# @file：narutomcomments.py
# @author：Hedian
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：火影忍者视频获取评论的文件
##############################################################r################################

import json
import math
import datetime
from configuration import constant 
from website.common.comments import SiteComments

from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.common import Common
from log.spiderlog import Logger
from utility.timeutility import TimeUtility

##############################################################################################
# @class：NarutomVideoComments
# @author：Hedian
# @date：2016/11/20
# @note：火影忍者获取评论的类，继承于SiteComments类
##############################################################################################
class NarutomVideoComments(SiteComments):
    COMMENTS_URL = 'http://narutom.duoshuo.com/api/threads/listPosts.json?source=duoshuo&thread_id={threadid}&order=desc&limit={limit}&page={page}'
    DEFAULT_PAGE_SIZE = 100
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/20
    # @note：NarutomVideoComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：NarutomVideoComments的入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
	try:
	    if params.step is NarutomVideoComments.STEP_1:
		self.step1(params)
	    elif params.step == NarutomVideoComments.STEP_2:
		self.step2(params)
	    elif params.step == NarutomVideoComments.STEP_3:
		self.step3(params)
	except:
	    Logger.printexception()
    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        #1. 根据输入原始url, 拼出评论首页
        encurl = Common.urlenc(params.originalurl)
        comments_url = 'http://narutom.duoshuo.com/api/threads/listPosts.json?url={url}&limit=1&page=1'.format(url=encurl)
        self.storeurl(comments_url, params.originalurl, NarutomVideoComments.STEP_2)

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        jsondata = json.loads(params.content)
        if 'thread' not in jsondata:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return 
        threadid = jsondata['thread']['thread_id']
        curcmtnum = int(jsondata['cursor']['total'])
        # 检查是否有评论数，没有，返回
        if int(curcmtnum) == 0:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return
        # 检查评论数是否增加，没有增加，返回；有增加，更新增加后的页面评论量
        curcmtnum = int(curcmtnum)
        NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        if dbcmtnum >= curcmtnum:
            return
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.DEFAULT_PAGE_SIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
        for page in range(1, pages + 1, 1):
            url = NarutomVideoComments.COMMENTS_URL.format(threadid=threadid, limit=NarutomVideoComments.DEFAULT_PAGE_SIZE, page=page)
            self.storeurl(url, params.originalurl, NarutomVideoComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        jsondata = json.loads(params.content)
        if 'parentPosts' not in jsondata:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return 
        parentPosts = jsondata['parentPosts']     
        for item in parentPosts:
	    curtime = item['created_at']
	    content = item['message']
	    CMTStorage.storecmt(params.originalurl, content, curtime, '')
	    
    
