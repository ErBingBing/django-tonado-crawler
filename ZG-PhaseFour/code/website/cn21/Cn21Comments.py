# coding=utf-8
##############################################################################################
# @file：Cn21Comments.py
# @author：Ninghz
# @date：2016/11/16
# @note：21CN获取评论的文件
##############################################################################################
import re
import urllib
import json
import math
from utility.timeutility import TimeUtility
from utility.common import Common
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from website.common.comments import SiteComments
##############################################################################################
# @class：Comments
# @author：Ninghz
# @date：2016/11/16
# @note：21CN获取评论的类，继承于SiteComments类
##############################################################################################
class Comments(SiteComments):
    COMMENTS_URL = 'http://review.21cn.com/review/list.do?operationId=%s&contentId=%s&pageNo=%d&pageSize=%d&sys=cms&order=new'
    PAGE_SIZE = 10.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/11/16
    # @note：Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/11/16
    # @note：Step1：通过共通模块传入的html内容获取到operaId，contentId，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                # 从html源码中获取拼接评论url的参数
                operaId = self.r.getid('operaId', params.content, '\s*:\s*')
                contentId = self.r.getid('contentId', params.content, '\s*:\s*')
                # 拼接第一页评论url
                comments_url = Comments.COMMENTS_URL % (operaId, contentId, 1, Comments.PAGE_SIZE)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, Comments.STEP_2, {'operaId':operaId, 'contentId':contentId})

            #获取第一页评论内容，循环获取全部评论url
            elif params.step == Comments.STEP_2:
		self.step2(params)

            #解析评论数据
            elif params.step == Comments.STEP_3:
		self.step3(params)
	except:
	    Logger.printexception()
	      
    #----------------------------------------------------------------------
    def step2(self, params):
	operaId = params.customized['operaId']
	contentId = params.customized['contentId']
	# 获取评论的Jason返回值
	comments = json.loads(params.content)
	# 获取评论页数
	curcmtnum = int(comments['pageTurn']['rowCount'])
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGE_SIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
	# 循环拼接评论url，提交下载平台获取评论数据
	for page in range(1, pages + 1, 1):
	    if page == 1:
		self.step3(params)
	    commentUrl = Comments.COMMENTS_URL % (operaId, contentId, page, Comments.PAGE_SIZE)
	    self.storeurl(commentUrl, params.originalurl, Comments.STEP_3, {'operaId':operaId, 'contentId':contentId})

    def step3(self, params):
	commentsinfo = json.loads(params.content)
	for comment in commentsinfo['list']:
	    try:
		curtime = comment['createTime']
		content = comment['reviewContent']
		CMTStorage.storecmt(params.originalurl, content, curtime, '')
	    except:
		Logger.printexception()
    