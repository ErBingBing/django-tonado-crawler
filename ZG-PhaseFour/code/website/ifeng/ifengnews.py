# -*- coding: utf-8 -*-
################################################################################################################
# @file: Ifengnewscomments.py
# @author：Liuyonglin
# @date：2016/12/12
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import json
import math
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.common import Common
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import getuniformtime
from storage.newsstorage import NewsStorage
from configuration import constant 
################################################################################################################
# @class：IfengNewsComments
# @author：Liuyonglin
# @date：2016/12/12
# @note：
################################################################################################################
class IfengNewsComments(SiteComments):
    COMMENTS_URL = 'http://comment.ifeng.com/get.php?doc_url={oriurl}&job=1&p={pg}&pageSize={ps}'
    # 凤凰新闻S1需要的类变量
    IFENG_NEWS_FIRST_PAGE = 'IFENG_NEWS_FIRST_PAGE'
    IFENG_NEWS_NEXT_PAGE = 'IFENG_NEWS_NEXT_PAGE'
    STEP2_XIAOBG = 'step1'
    post_url = 'http://comment.ifeng.com/getspecial?job=1&order=DESC&orderBy=create_time&format=json&pagesize=20'
    comment_xiaobgurl = 'http://finance.ifeng.com/xiaobg/special/xiaobg98/'
    post_data = {}


    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：IfengNewsComments，初始化内部变量
    ################################################################################################################
    def __init__(self, parent=None):
        SiteComments.__init__(self)
        self.page_size = 20
	if parent:
	    self.website = parent.website
    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == None:
            if self.r.search('https?://finance\.ifeng\.com/.*/special/(xiaobg.*|bjczbf)',params.originalurl):
                self.step1_ifeng_xiaobg(params)
            else:
		self.ifengnews_step1(params)
        elif params.step == IfengNewsComments.IFENG_NEWS_FIRST_PAGE:
            self.ifengnews_step2(params)
        elif params.step == IfengNewsComments.IFENG_NEWS_NEXT_PAGE:
            self.ifengnews_step3(params)     
        elif params.step == IfengNewsComments.STEP2_XIAOBG:
            self.step2_ifeng_xiaobg(params)
        
    ################################################################################################################
    # @functions：ifengnews_step1
    # @info： 获取评论
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def ifengnews_step1(self, params):
        try:
	    oriurl = self.r.getid('commentUrl', params.content, ':')
	    if oriurl.startswith('http'):
		oriurl = Common.urlenc(oriurl)
	    if not oriurl:
		oriurl = self.r.getid('vid', params.content, split=':')
	    if not oriurl:
		Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
		return
	    commentinfo_url = IfengNewsComments.COMMENTS_URL.format(oriurl=oriurl, pg=1, ps=self.page_size)
	    self.storeurl(commentinfo_url, params.originalurl, IfengNewsComments.IFENG_NEWS_FIRST_PAGE,{'oriurl':oriurl})
        except:
            Logger.printexception()

    ################################################################################################################
    # @functions：ifengnews_step2
    # @info： 获取评论
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def ifengnews_step2(self, params):
        try:
	    oriurl = params.customized['oriurl']
            jsoncontent = json.loads(params.content)
	    clicknum = float(jsoncontent.get('join_count', '-1'))
	    if clicknum > 0:
		NewsStorage.setclicknum(params.originalurl, clicknum)	    
            curcmtnum = float(jsoncontent['count'])
	    NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	    dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	    if dbcmtnum >= curcmtnum:
		return    
	    # 循环取得评论的url
	    pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
	    if pages >= self.maxpages:
		pages = self.maxpages            
            # 拼出第一页之外的其他所有评论url
            for index in range(1, pages+1, 1):
                if index == 1:
                    self.ifengnews_step3(params)
                    continue
                commentinfo_url = IfengNewsComments.COMMENTS_URL.format(oriurl=oriurl, pg=index,ps=self.page_size)
                self.storeurl(commentinfo_url, params.originalurl, IfengNewsComments.IFENG_NEWS_NEXT_PAGE)
        except:
            Logger.printexception()

    ################################################################################################################
    # @functions：ifengnews_step3
    # @info： 获取评论
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def ifengnews_step3(self, params):
        try:
            # Step3: 通过Step2设置的url，得到所有评论，抽取评论
            jsoncontent = json.loads(params.content)
            # "count":491,"join_count":3832,"comments":false,"allow_comment":1
            if type(jsoncontent['comments']) == bool:
                return
            for comment in jsoncontent['comments']:
                # 提取评论内容
                content = comment['comment_contents']
                # 提取时间
                publicTime = comment['comment_date']
                # 提取昵称
                nickname = comment['uname']
                if not CMTStorage.exist(params.originalurl, content, publicTime, nickname):
                    CMTStorage.storecmt(params.originalurl, content, publicTime, nickname)
        except:
            Logger.printexception()
            
    #----------------------------------------------------------------------
    def step1_ifeng_xiaobg(self,params):
        pattern = '\"url\": \"(.*)\".*\summary'
        if self.r.search(pattern, params.content):
            IfengNewsComments.post_data["docurl"] = self.r.parse(pattern, params.content)
        else:
	    IfengNewsComments.post_data["docurl"] = IfengNewsComments.comment_xiaobgurl
        IfengNewsComments.post_data["p"] = '1'
	Logger.getlogging().debug('url:{url}'.format(url=IfengNewsComments.post_url))
	Logger.getlogging().debug('data:{data}'.format(data=str(IfengNewsComments.post_data)))
        self.storeposturl(IfengNewsComments.post_url, params.originalurl, self.STEP2_XIAOBG, IfengNewsComments.post_data)
        
    def step2_ifeng_xiaobg(self, params):
        try:
            jsoncontent = json.loads(params.content)
	    clicknum = float(jsoncontent.get('join_count', '-1'))
	    if clicknum > 0:
		NewsStorage.setclicknum(params.originalurl, clicknum)	    
	    curcmtnum = jsoncontent['count']
	    NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	    dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	    if dbcmtnum >= curcmtnum:
		return    
	    # 循环取得评论的url
	    pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
	    if pages >= self.maxpages:
		pages = self.maxpages	    
            for index in range(1, pages+1, 1):
		if index == 1:
		    self.ifengnews_step3(params)
		    continue
                self.post_data['p'] = index
                self.storeposturl(self.post_url, params.originalurl, 
                                  self.IFENG_NEWS_NEXT_PAGE, IfengNewsComments.post_data)
        except:
            Logger.printexception()   
        
        