# coding=utf8
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
from bs4 import BeautifulSoup 
########################################################################
class YeyouComments(SiteComments):
    """"""
    #http://comment2.17173.com/front/comment/list.do?sid=10076258_1_90095&pageSize=20&pageNo=1&sort=1
    #http://news.yeyou.com/content/09132017/085046056.shtml
    COMMENT_URL = 'http://comment2.17173.com/front/comment/list.do?sid={sid}&pageSize={pagesize}&pageNo={pageno}&sort=1'
    PAGESIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    #----------------------------------------------------------------------
    def __init__(self):
        SiteComments.__init__(self)
        
    def process(self, params):
        try:
            if params.step is self.STEP_1:
                self.step1(params)
            elif params.step == self.STEP_2:
		self.step2(params)
            elif params.step == self.STEP_3:
                self.step3(params)
        except:
            Logger.printexception()	        
    #----------------------------------------------------------------------
    def step1(self, params):
        sid = self.r.getid('data-widget-sid', params.content, split='=')
        url = self.COMMENT_URL.format(sid=sid, pagesize=self.PAGESIZE, pageno=1)
        self.storeurl(url, params.originalurl, self.STEP_2, {"sid": sid})
        
    #----------------------------------------------------------------------
    def  step2(self, params):
        sid = params.customized['sid']
        jsdata = json.loads(params.content)
        data = jsdata['data']
        curcmtnum = data['totalCount']
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGESIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
	for page in range(1, pages + 1, 1):
	    if page == 1:
		self.step3(params)
		continue
	    url = self.COMMENT_URL.format(sid=sid, pagesize=self.PAGESIZE, pageno=page)
            self.storeurl(url, params.originalurl, self.STEP_3, {"sid": sid})
    #----------------------------------------------------------------------
    def step3(self, params):
	jsdata = json.loads(params.content)
	listdata = jsdata['data']['listData'] 
	for data in listdata:
	    try:
		curtime = data['createTime']
		content = data['content']
		CMTStorage.storecmt(params.originalurl, content, curtime, '')
	    except:
		Logger.printexception()
            
        
        
        
        
        
        
        
    
    