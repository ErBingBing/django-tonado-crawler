# coding=utf8
##############################################################################################
# @file：ChangyanComments.py
# @author：Liyanrui
# @date：2016/11/21
# @version：Ver0.0.0.100
# @note：畅言获取评论的文件
###############################################################################################

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
from utility.xpathutil import XPathUtility 
from configuration import constant
##############################################################################################
# @class：ChangyanComments
# @author：Liyanrui
# @date：2016/11/21
# @note：畅言获取评论的类，继承于SiteComments类
##############################################################################################
class ChangyanComments(SiteComments):
    # 评论首页URL
    #LITELOAD_URL = 'http://changyan.sohu.com/api/{liteloadApi}topic/liteload?client_id={client_id}&topic_source_id={topic_category_id}'
    LITELOAD_URL = 'http://changyan.sohu.com/api/{liteloadApi}/topic/liteload?client_id={client_id}&topic_url={topic_url}&topic_source_id={topic_source_id}'
    # 评论分页URL
    COMMENTS_URL = 'http://changyan.sohu.com/api/{commentsApi}/topic/comments?client_id={client_id}&page_no={page_no}&page_size={page_size}&topic_id={topic_id}'
    #COMMENTS_URL = 'http://changyan.sohu.com/api/{liteloadApi}/topic/liteload?client_id={client_id}&topic_url={topic_url}&topic_category_id={topic_category_id}&page_size={page_size}&topic_source_id={topic_source_id}'
    # 共通参数
    PAGE_SIZE = 30
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    FLG = True
    __instance = None
    liteloadApi = 3
    commentsApi = 2
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/21
    # @note：畅言类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent = None):
        SiteComments.__init__(self)
	if parent:
	    self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：params：评论的文本内容
    #          topicSourceId：获取评论url的topicSourceId
    #          liteloadApi: 首页评论url的Api参数
    #          commentsApi：所有评论url的Api参数
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：params：评论文本内容
    #        topicSourceId：调用模块传入
    #        liteloadApi：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        commentsApi：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def getcomments(self, params, topic_source_id=None, liteloadApi=None,commentsApi=None):
        try:
            if params.step is ChangyanComments.STEP_1:
                self.step1(params)
            elif params.step == ChangyanComments.STEP_2:
		self.step2(params)
            elif params.step == ChangyanComments.STEP_3:
                self.step3(params)
        except:
            Logger.printexception()
	    
    def process(self, params):
        try:
            if params.step is ChangyanComments.STEP_1:
                self.step1(params)
            elif params.step == ChangyanComments.STEP_2:
		self.step2(params)
            elif params.step == ChangyanComments.STEP_3:
                self.step3(params)
        except:
            Logger.printexception()	
	    
    def step1(self, params):
	if re.search('http://.*\.sohu\.com/', params.originalurl):
	    cmttext = XPathUtility(params.content).getstring('//*[@class="c-num-red"][2]|//*[@id="changyan_parti_unit"]|//*[@class="remark-tit"]')
	    if cmttext:
		try:
		    cmtnum = re.findall('\d+', cmttext)[0]
		except:
		    cmtnum = -1
	    else:
		cmtnum = -1
	    #cmtnum = NewsStorage.getcmtnum(params.originalurl)
	    if int(cmtnum) == -1:
		pass
	    elif int(cmtnum) == 0:
		Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
		return
	else:
	    cmttext = XPathUtility(params.content).xpath('//*[@class="prompt-null-w"]')
	    if cmttext:
		Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
		return
	liteloadApi = ChangyanComments.liteloadApi
	commentsApi = ChangyanComments.commentsApi
	# 取得client_id
	if re.match('http://\w+\.sohu\.com.*',params.originalurl):
	    client_id = 'cyqemw6s1'
	elif re.match(r'^http://\w+\.(17173|shouyou|yeyou)\.com/.*',params.originalurl):
	    client_id = 'cyqvqDTV5'
	elif re.match(r'^http://sports\.le\.com/.*', params.originalurl):
	    client_id = 'cyrJ22d8v'
	#针对妆点网做特殊处理
	elif re.match(r'^http://\w+\.zdface\.com.*', params.originalurl):
	    client_id = 'cyrJOywnM'
	#http://xx.yzz.cn/xiuba/201609/1017135.shtml
	elif re.match(r'^http://\w+\.yzz\.cn.*', params.originalurl):
	    client_id = 'cyrtYf3sa'
	elif re.match(r'^http://\w+\.178\.com.*', params.originalurl):
	    client_id = 'cysrntF12'
	elif re.match(r'^http://.*\.cyol\.com/.*', params.originalurl):
	    client_id = 'cys3X3zo9'
	else:
	    client_id = self.r.getid('appid', params.content)
	topic_url = urllib.quote_plus(params.originalurl)
	#LITELOAD_URL = 'http://changyan.sohu.com/api/{liteloadApi}/topic/liteload?client_id={client_id}&topic_url={topic_url}&topic_source_id={topic_source_id}'
	topic_source_id = self.r.getid('sid',params.content)
	if not topic_source_id:
	    topic_source_id = self.r.getid('data-widget-sid', params.content)
	comment_url = ChangyanComments.LITELOAD_URL.format(liteloadApi=liteloadApi, client_id=client_id, topic_url=topic_url, topic_source_id=topic_source_id) 
	self.storeurl(comment_url, params.originalurl, ChangyanComments.STEP_2, {'client_id': client_id,
	                                                                         'liteloadApi':liteloadApi, 
	                                                                         'topic_url':topic_url, 
	                                                                         'commentsApi':commentsApi})	
	    
    def step2(self, params):
	# 取得client_id
	liteloadApi  = params.customized['liteloadApi']
	client_id  = params.customized['client_id']
	topic_url  = params.customized['topic_url']
	commentsApi = params.customized['commentsApi']
	# 取得评论个数
	content = json.loads(params.content)
	curcmtnum = float(content.get('cmt_sum',0))
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return
	# 取得topicId
	topic_id = content.get('topic_id','')
	if not topic_id:
	    Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
	    return
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / ChangyanComments.PAGE_SIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
	for page in range(1, pages + 1, 1):
	    # 取得评论的url
	    #COMMENTS_URL = 'http://changyan.sohu.com/api/{commentsApi}/topic/comments?client_id={client_id}&page_no={page_no}&page_size={page_size}&topic_id={topic_id}'	    
	    url = ChangyanComments.COMMENTS_URL.format(commentsApi=commentsApi,
	                                               client_id=client_id, 
	                                               page_no = page,
	                                               page_size = ChangyanComments.PAGE_SIZE,
	                                               topic_id=topic_id,
	                                               )
	    self.storeurl(url, params.originalurl, ChangyanComments.STEP_3)
	
    #----------------------------------------------------------------------
    def  step3(self,params):
        """通过评论的url获取评论"""
        try:
            jsondata = json.loads(params.content)
            if jsondata['comments']:
                for comment in jsondata['comments']:
                    content = comment['content']
                    curtime = TimeUtility.getuniformtime(comment['create_time'])
                    nick = comment['passport'].get('nickname','anonymous')
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                    reply = comment['comments']
                    while reply:
                        for comment in comment['comments']:
                            content = comment['content']
                            curtime = TimeUtility.getuniformtime(comment['create_time'])
                            nick = comment['passport'].get('nickname','anonymous')
                            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                            reply = comment['comments']
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))

    @staticmethod
    def getinstance():
        if ChangyanComments.__instance is None:
            ChangyanComments.__instance = ChangyanComments()
        return ChangyanComments.__instance
