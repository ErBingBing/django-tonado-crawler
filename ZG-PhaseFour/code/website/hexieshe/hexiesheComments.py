# encoding=utf8

##############################################################################################
# @file：HexiesheComments.py
# @author：HuBorui
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：爱美女性网获取评论的文件
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
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup 
##############################################################################################
# @class：HexiesheComments
# @author：HuBorui
# @date：2016/11/30
# @note：爱美女性网获取评论的类，继承于WebSite类
##############################################################################################
class HexiesheComments(SiteComments):
    COMMENT_URL = 'https://www.hexieshe.com/{tid}/comment-page-{page}/#comments'
    STEP_1_BBS = None
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'
    PAGESIZE = 50
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/30
    # @note：HexiesheComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：HexiesheComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step == HexiesheComments.STEP_1_BBS:
                self.step1bbs(params)
            elif params.step == HexiesheComments.STEP_2_BBS:
                self.step2bbs(params)
        except:
	    Logger.printexception()

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step1bbs(self, params):
        tid = self.r.getid('www.hexieshe.com', params.originalurl, split='/')
        curcmtnum = XPathUtility(params.content).getnumber('//*[@id="mh-comments"]/h4')
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGESIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
	for page in range(1, pages+1, 1):
	    if page == 1:
		self.step2bbs(params)
		continue
	    comment_url = HexiesheComments.COMMENT_URL.format(tid=tid, page=page)
	    self.storeurl(comment_url, params.originalurl, HexiesheComments.STEP_2_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step2bbs(self, params):
	soup = BeautifulSoup(params.content, 'html5lib')
	lis = soup.find_all(attrs={'id': re.compile('comment-\d+')})
	for li in lis:
	    try:
		curtime = li.select_one('.mh-comment-meta-date').get_text()
		curtime = TimeUtility.getuniformtime(curtime)
		content = li.select_one('.mh-comment-content').get_text()
		CMTStorage.storecmt(params.originalurl, content, curtime, '')
	    except:
		Logger.printexception()	    