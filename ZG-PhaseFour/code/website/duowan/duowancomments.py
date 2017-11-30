# encoding=utf-8
##############################################################################################
# @file：duowancomments.py
# @author：Ninghz
# @date：2016/11/28
# @note：多玩获取评论的文件
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
from utility.bbs2commom import CommenComments
##############################################################################################
# @class：DuowanComments
# @author：Ninghz
# @date：2016/11/28
# @note：多玩网站获取评论的类，继承于SiteComments类
##############################################################################################
class DuowanComments(SiteComments):
    COMMENTS_URL = 'http://comment3.duowan.com/index.php?r=comment/comment&order=time&noimg=true&uniqid=%s&domain=%s&url=%s&num=%d'
			 #'http://comment3.duowan.com/index.php?r=comment/totaljson&uniqid={uniqid}&domain=www.duowan.com&url=%2F1610%2F339705787366.html'
    COMMENT_COUNTS_URL = 'http://comment3.duowan.com/index.php?r=comment/totaljson&uniqid=%s&domain=%s&url=%s'
    BBS_TITLE = ''
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2_BBS = '2_bbs'
    STEP_2 = 2
    STEP_2_TU = '2_tu'
    STEP_3_BBS = '3_bbs'
    STEP_3 = 3


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/11/28
    # @note：DuowanComments类的构造器，初始化内部变量
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
    # @date：2016/11/28
    # @note：Step1：通过共通模块传入的html内容获取到oid，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            field = self.r.parse('^http://(\w+)\.duowan\.com*', params.originalurl)[0]
            if field == 'bbs':
                CommenComments(self).process(params)
                return
            if params.step is None:
                self.step1(params)
            elif params.step == DuowanComments.STEP_2_TU:
                self.step_tu(params)
                # 获取评论总数，拼接所有评论url
            elif params.step == DuowanComments.STEP_2:            
                self.step2(params)
            elif params.step == DuowanComments.STEP_3:    
                self.step3(params)
        except:
            Logger.printexception()
            
    def step1(self, params):
        field = self.r.parse('^http://(\w+)\.duowan\.com*', params.originalurl)[0]
        if field == 'video':
            if self.r.parse('qianwangbieyongzhegebianliang_domain\s*=\s*\"(.*?)\";',params.content).__len__()>0:
                domain = self.r.parse('qianwangbieyongzhegebianliang_domain\s*=\s*\"(.*?)\";',params.content)[0]
                pUrl = self.r.parse('qianwangbieyongzhegebianliang_url\s*=\s*\"(.*?)\";',params.content)[0]
            else:
                domainUrl = params.originalurl[7:params.originalurl.__len__()]
                domain = domainUrl[0:domainUrl.index('/')]
                pUrl = domainUrl[domainUrl.index('/'):domainUrl.index('.html') + 5]                
        else:
            domainUrl = params.originalurl[7:params.originalurl.__len__()]
            domain = domainUrl[0:domainUrl.index('/')]
            pUrl = domainUrl[domainUrl.index('/'):domainUrl.index('.html')+5]            

        # 图片
        if field == 'tu':
            getByGallery_url = 'http://tu.duowan.com/index.php?r=show/getByGallery/&gid=' + domainUrl[domainUrl.rfind('/')+1:domainUrl.index('.html')]
            Logger.getlogging().debug(getByGallery_url)
            self.storeurl(getByGallery_url, params.originalurl, DuowanComments.STEP_2_TU, {'domain' : domain, 'pUrl' : pUrl})
        else:
            uniqid = self.r.getid('comment3Uniqid', params.content, '\s*=\s*')
            # 拼接总评论数的url
            comment_counts_url = DuowanComments.COMMENT_COUNTS_URL % (uniqid, domain, pUrl)
            self.storeurl(comment_counts_url, params.originalurl, DuowanComments.STEP_2, {'uniqid': uniqid, 'domain' : domain, 'pUrl' : pUrl})        
        
        #new video,need to find real originalurl,so real_originalurl=originalurl.replace('.com','.cn') 
        soup = BeautifulSoup(params.content, 'html5lib')
        if soup.select_one('#dw-video-wrap'):
            real_originalurl = params.originalurl.replace('.com','.cn')
            self.storeurl(real_originalurl, params.originalurl, DuowanComments.STEP_1)
        clicknumobj = soup.select_one('.vcol-main-hd > strong')
        if clicknumobj:
            clicknum = clicknumobj.get_text()
            clicknum = self.str2num(clicknum)
            NewsStorage.setclicknum(params.originalurl, clicknum)

    def step_tu(self, params):
        # 图片模块独有，获取uniqid集合，循环拼接出评论url
        domain = params.customized['domain']
        pUrl = params.customized['pUrl']
        uniqidinfo = json.loads(params.content)
        for picInfo in uniqidinfo['picInfo']:
            commentUrl = DuowanComments.COMMENT_COUNTS_URL % (picInfo['cmt_md5'], domain, pUrl)
            self.storeurl(commentUrl, params.originalurl, DuowanComments.STEP_2, { 'uniqid' : picInfo['cmt_md5'], 'domain': domain, 'pUrl': pUrl })

    def step2(self, params):
        uniqid = params.customized['uniqid']
        domain = params.customized['domain']
        pUrl = params.customized['pUrl']
        # 获取评论总数的Jason返回值
        commentsinfo = json.loads(params.content)
        # 评论总数
        curcmtnum = float(commentsinfo['show']['total_num'])
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGE_SIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages
	for page in range(0, pages, 1):
            commentUrl = DuowanComments.COMMENTS_URL % (uniqid, domain, pUrl, page * self.PAGE_SIZE)
            self.storeurl(commentUrl, params.originalurl, DuowanComments.STEP_3)        

    def step3(self, params):
        # 获取评论的Jason返回值
        commentsinfo = json.loads(params.content)
        for comment in commentsinfo:
	    curtime = comment['created']
	    content = comment['contents']
	    CMTStorage.storecmt(params.originalurl, content, curtime, '')
  
        
  