# encoding=utf8

##############################################################################################
# @file：hupuComments.py
# @author：HuBorui
# @date：2016/11/29
# @version：Ver0.0.0.100
# @note：虎扑网获取评论的文件
##############################################################################################
import re
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from configuration import constant 
##############################################################################################
# @class：hupuComments
# @author：HuBorui
# @date：2016/11/29
# @note：虎扑网获取评论的类，继承于WebSite类
##############################################################################################
class hupuComments(SiteComments):
    COMMENT_URL = 'https://bbs.hupu.com/{docurl}-{page}.html'
    STEP_1 = None
    STEP_1_2 = '1_2'
    STEP_2 = '2_1'
    
    page_size = 20
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/29
    # @note：hupuComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：HuBorui
    # @date：2016/11/29
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is hupuComments.STEP_1:
                self.step1(params)
            elif params.step == hupuComments.STEP_1_2:
                self.step1_2(params)	    
            elif params.step == hupuComments.STEP_2:
                self.step2(params)
        except:
            Logger.printexception()
        
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        #Step1: 通过得到docurl，得到获取评论的url的参数。
        #docurl = self.r.parse('^http://bbs\.hupu\.com\/(\d+)', params.originalurl)
        docurl = self.r.parse('^http[s]{0,1}://bbs\.hupu\.com\/(\d+)', params.originalurl)
        if docurl:
            docurl = docurl[0]
        else:
            Logger.getlogging().debug('{url}:20000'.format(url=params.originalurl))
            return
        # 取得正文
        xparser = XPathUtility(params.content)
        #取得页数
	pageList = xparser.getcomments('//div[@class="page"]/a')
        if not pageList:
            pagenum = 1
        elif pageList:
            pagenum = pageList[-2]
        else:
            return
        if int(pagenum) >= self.maxpages:
            pagenum = self.maxpages
        # 评论总数
        curcmtnum = xparser.getnumber('//span[@class="browse"]')
	NewsStorage.setcmtnum(params.originalurl, curcmtnum)
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
		return

	start = int(dbcmtnum / self.page_size) + 1
	end = int(pagenum)
	if end > start+ self.maxpages:
		start =  end - self.maxpages

	params.customized['page'] = 1
	if end == 1:
		self.step2(params)
		return
	if start == 1:
		self.step2(params)
	comment_url = self.COMMENT_URL.format(docurl=docurl, page=end)
	self.storeurl(comment_url, params.originalurl, hupuComments.STEP_1_2,{'docurl':docurl, 'page':end,
	                                                                    'start':start, 'end':end})   
	    
    #----------------------------------------------------------------------
    def step1_2(self,params):
	#最后一页
	page = params.customized['page']
	start = params.customized['start']
	end = params.customized['end']
	docurl = params.customized['docurl']
	for page in range(end, start-1, -1):
	    if int(page) == end:
		if not self.step2(params):
		    break
		continue
	    if int(page) == 1:
		continue
	    comment_url = self.COMMENT_URL.format(docurl=docurl, page=page)
	    self.storeurl(comment_url, params.originalurl, self.STEP_2,{'page':page})        
    
    #----------------------------------------------------------------------
    def step2(self,params):
        page = params.customized['page']
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        soup = BeautifulSoup(params.content, 'html5lib')
	divs = soup.select('#t_main > .floor')
        if page == 1:
	    divs = divs[1:]
	publishlist = []
	for div in divs:
	    try:
		curtime = div.select_one('.stime').get_text()
		content = div.select_one('.case').get_text()
		CMTStorage.storecmt(params.originalurl, content, curtime, '')
		publishlist.append(curtime)
	    except:
		Logger.printexception()
	if not self.isnewesttime(params.originalurl, min(publishlist)):
	    return False
	return True