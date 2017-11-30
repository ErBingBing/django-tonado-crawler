# coding=utf-8
##############################################################################################
# @file：huxiuComments.py
# @author：Ninghz
# @date：2016/12/13
# @note：虎嗅获取评论的文件
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
from configuration import constant
from bs4 import BeautifulSoup 

##############################################################################################
# @class：huxiuS2Comments
# @author：
# @date：
# @note：
##############################################################################################
class HuxiupostComments(SiteComments):
    # 资讯模块
    POST_URL = 'https://www.huxiu.com/comment/getCommentList'
    POST_DATA = {'object_type':1, 
                 'object_id':'', 
                 'type':2, 
                 'page':0}
    COMMONURL = 'https://www.huxiu.com/comment/getCommentList?object_type=1&type=2&object_id={object_id}&page={page}'
    EACH = 'each'
    page_size = 20
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：
    # @date：
    # @note：huxiuComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self,parent=None):
        SiteComments.__init__(self)
            
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/12/13
    # @note：Step1：通过共通模块传入的html内容获取到operaId，contentId，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                self.step1(params)
            if params.step == HuxiupostComments.EACH:
                self.step2(params)
        except:
            Logger.printexception()
            
    #----------------------------------------------------------------------
    def step1(self,params):
	pattern = 'https://www.huxiu.com/article/(\d+).html'
	if not self.r.search(pattern, params.originalurl):
	    Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
	    return 
	else:
	    object_id = self.r.parse(pattern, params.originalurl)[0]
	curcmtnum = XPathUtility(params.content).getnumber('//*[@class="article-pl pull-left"]')
	if not curcmtnum:
	    Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_COMMNETS)
	    return 
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
	if pages >= self.maxpages:
	    pages = self.maxpages
        for page in range(1,pages+1):
            #self.POST_DATA['object_id'] = object_id
	    #self.POST_DATA['page'] = page
            #self.storeposturl(self.POST_URL, params.originalurl, HuxiupostComments.EACH, self.POST_DATA)
	    commonurl = self.COMMONURL.format(object_id=object_id, page=page)
	    self.storeurl(commonurl, params.originalurl, HuxiupostComments.EACH)
                                          
    #----------------------------------------------------------------------
    def step2(self,params):
        # comments = params.content[params.content.index("{"):params.content.rindex("}")+1]
        jsdata = json.loads(comments)
        content = jsdata['data']['data']
        soup = BeautifulSoup(content,'html5lib')
        divs = soup.find_all(attrs={'id':'g_pid', 'class':'pl-box-wrap'})
        if not divs:
            Logger.log(params.url, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return
        for div in divs:
            try:
                curtime = div.select_one('.comment-yh-time').get_text()
                comment = div.find(attrs={'class': 'pl-content pl-yh-content'}).get_text()
                CMTStorage.storecmt(params.originalurl, comment, curtime, '')
            except:
                 Logger.printexception()

        
        
