# encoding=utf-8
##############################################################################################
# @file：U17NewsComments.py
# @author：Liuyonglin
# @date：2016/12/08
# @version：Ver0.0.0.100
# @note：有妖气获取评论的文件
###############################################################################################
import re
import urllib
import json
import math
from  configuration import constant 
from utility.timeutility import TimeUtility
from utility.common import Common
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from website.common.comments import SiteComments
from bs4 import BeautifulSoup 
##############################################################################################
# @class：U17NewsComments
# @author：Liuyonglin
# @date：2016/12/08
# @note：有妖气获取评论的类，继承于WebSite类
##############################################################################################
class U17NewsComments(SiteComments):
    COMMENT_URL_NEWS = 'http://www.u17.com/comment/ajax.php?mod=thread&act=get_comment_php_v4&sort=create_time&thread_id={threadid}&object_id={objectid}&page={page}&page_size={pagesize}&face=small&comic_id={comicid}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：U17NewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.page_size = 20
        self.website = parent.website
        self.pid = 1

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is U17NewsComments.STEP_1:
                self.step1news(params)
            elif params.step == U17NewsComments.STEP_2:
                self.step2news(params)
            elif params.step == U17NewsComments.STEP_3:
                self.step3news(params)
            else:
                Logger.getlogging().error('params.step == {step}'.format(step=params.step))
                return
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step1news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1news(self, params):
	if not self.r.search('^http://www\.u17\.com\/comic\/(\d+)\.html', params.originalurl):
	    Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
	    return
        docurl = self.r.parse('^http://www\.u17\.com\/comic\/(\d+)\.html', params.originalurl)[0]
        threadid = self.r.getid('thread_id',params.content)
        # 评论首页URL
        commentinfo_url = U17NewsComments.COMMENT_URL_NEWS.format(threadid=threadid, objectid=docurl, page=1, pagesize=self.page_size, comicid = docurl)
        self.storeurl(commentinfo_url, params.originalurl, U17NewsComments.STEP_2)

    ##############################################################################################
    # @functions：step2news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2news(self, params):
        curcmtnum = self.r.parse("\"total\"\:(\d+)", params.content)[0]
        page_count = self.r.parse("\"total_page\"\:(\d+)", params.content)[0]
        threadid = self.r.parse("\"thread_id\"\:\"(\d+)\"",params.content)[0]
        objectid = self.r.parse("\"object_id\"\:\"(\d+)\"",params.content)[0]
	curcmtnum = int(curcmtnum)
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
	if pages >= self.maxpages:
	    pages = self.maxpages
	for page in range(1, pages + 1, 1):
	    if page == 1:
		self.step3news(params)
		continue
            comment_url = U17NewsComments.COMMENT_URL_NEWS.format(threadid=threadid, objectid=objectid, page=page, pagesize=self.page_size, comicid = objectid)
            self.storeurl(comment_url, params.originalurl, U17NewsComments.STEP_3)

    ##############################################################################################
    # @functions：step3news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3news(self, params):
        soup = BeautifulSoup(params.content, 'html5lib')
        divs = soup.select('.ncc_content')
	for div in divs:
	    content = div.select_one('.ncc_content_right_text').get_text()
	    curtime = div.select_one('.ncc_content_right_title > dt').get_text()
	    CMTStorage.storecmt(params.originalurl, content, curtime, '')

            
            
