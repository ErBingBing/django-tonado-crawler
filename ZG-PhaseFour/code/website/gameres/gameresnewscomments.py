# encoding=utf8

##############################################################################################
# @file：GameresNewsComments.py
# @author：Liuyonglin
# @date：2016/12/13
# @version：Ver0.0.0.100
# @note：游资网获取评论的文件
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
# @class：GameresNewsComments
# @author：Liuyonglin
# @date：2016/12/13
# @version：Ver0.0.0.100
# @note：游资网获取评论的文件
##############################################################################################
class GameresNewsComments(SiteComments):
    COMMENTS_URL = 'http://www.gameres.com/forum.php?mod=viewthread&tid={docurl}&extra=page%3D1&from=portal&page={page}'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liuyonglin
    # @date：2016/12/13
    # @note：GameresNewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 10

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/13
    # @note：GameresNewsComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is GameresNewsComments.STEP_1:
                self.step1(params)
            elif params.step == GameresNewsComments.STEP_3:
                self.step3(params)
        except:
	    Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/13
    # @note：根据主页获取评论页，传入评论页，获取评论数
    ##############################################################################################
    def step1(self, params):
        if self.r.match('http://www.gameres.com/\d+.html', params.originalurl):
            docurl = self.r.parse('^http://www\.gameres\.com\/(\d+)', params.originalurl)[0]
            numtext = XPathUtility(params.content).getstring('//p[@class="xg1"]')
	    content = XPathUtility(params.content).xpath('//*[contains(@id,"postmessage")]/text()')[0]
	    NewsStorage.setbody(params.originalurl, content)
            curcmtnum = int(self.r.getid(u'评论数', params.content, split=':'))
            # 判断增量
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
		    self.step3(params)
		    continue
                commentinfo_url = GameresNewsComments.COMMENTS_URL.format(docurl = docurl, page = page)
                self.storeurl(commentinfo_url, params.originalurl, GameresNewsComments.STEP_3,{'page': page})
        else:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_TEMPLATE)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/13
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        soup = BeautifulSoup(params.content, 'html5lib')
        divs = soup.find_all(attrs={'id':re.compile('post_\d+')})
        for div in divs:
	    try:
		curtime = div.find(attrs={'class':'xg1 xw0'}).get_text()
		content = div.select_one('.t_f').get_text()
		CMTStorage.storecmt(params.originalurl, content, curtime, '')
	    except:
		Logger.printexception()
