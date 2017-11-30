# coding=utf-8

##############################################################################################
# @file：qiyiComments.py
# @author：Hedian
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：爱奇艺视频获取评论的文件
##############################################################r################################

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
# @class：IqiyiComments
# @author：Hedian
# @date：2016/11/20
# @note：爱奇艺获取评论的类，继承于SiteComments类
##############################################################################################
class IqiyiComments(SiteComments):
    COMMENTS_URL1 = 'http://api.t.iqiyi.com/qx_api/comment/get_video_comments?page={pageno}&page_size={pagesize}&qitanid={qitanid}&sort=add_time&tvid={tvid}'
    COMMENTS_URL2 = 'http://api.t.iqiyi.com/qx_api/comment/get_video_comments?page={pageno}&page_size={pagesize}&sort=add_time&tvid={tvid}'
    PLAYCOUNT_URL = 'http://cache.video.iqiyi.com/jp/pc/{tvid}/'
    DEFAULT_PAGE_SIZE = 100
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_PLAYCOUNT = 'PLAYCOUNT'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/20
    # @note：IqiyiComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        pass

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：IqiyiComments的入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is IqiyiComments.STEP_1:
                self.step1(params)
            elif params.step == IqiyiComments.STEP_2:
                self.step2(params)
            elif params.step == IqiyiComments.STEP_3:
                self.step3(params)
            elif params.step == IqiyiComments.STEP_PLAYCOUNT:
                self.geturlplaycount(params)            
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：
    # @date：2016/11/20
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        # 获取发布时间,正文
        pubtime = ''
        soup = BeautifulSoup(params.content, 'html5lib')
        pubTimes = self.r.getid('data-qitancomment-tvyear', params.content)
        if pubTimes:
            NewsStorage.setpublishdate(params.url, TimeUtility.getuniformtime(pubTimes))
       
        #1. 下载html，使用正则表达式获取data-qitancomment-qitanid字段
        qitanid = self.r.getid('data-qitancomment-qitanid', params.content)
        tvid = self.r.getid('data-qitancomment-tvid', params.content)
	playcounturl = self.PLAYCOUNT_URL.format(tvid=tvid)
	self.storeurl(playcounturl, params.originalurl, IqiyiComments.STEP_PLAYCOUNT, {'tvid': tvid})
        #2. 判断qitanid的值
        if qitanid and int(qitanid):
            # 2.1 qitanid不为0
            #2.1.1使用如下URL获取评论量
            comments_url = 'http://api.t.iqiyi.com/qx_api/comment/get_video_comments?page=1&page_size=1&qitanid={qitanid_value}&sort=add_time&need_total=1&tvid={tvid_value}'.format(qitanid_value=qitanid,tvid_value=tvid)
            self.storeurl(comments_url, params.originalurl, IqiyiComments.STEP_2, {'qitanid': qitanid, 'tvid': tvid})
        else:
            #2.2 如果data-qitancomment-qitanid=0
            #2.2.1. 下载html，使用正则表达式获取data-qitancomment-tvid字段
            comments_url = 'http://api.t.iqiyi.com/qx_api/comment/get_video_comments?page=1&page_size=1&sort=add_time&tvid={tvid_value}&need_total=1'.format(tvid_value=tvid)
            self.storeurl(comments_url, params.originalurl, IqiyiComments.STEP_2, {'qitanid': '0',  'tvid': tvid})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        qitanid = params.customized['qitanid']
        tvid = params.customized['tvid']
        comments = json.loads(params.content)
        curcmtnum = float(comments['data']['count'])
	NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
	dbcmtnum = CMTStorage.getcount(params.originalurl, True)
	if dbcmtnum >= curcmtnum:
	    return    
	# 循环取得评论的url
	pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.DEFAULT_PAGE_SIZE))
	if pages >= self.maxpages:
	    pages = self.maxpages  
        
	for page in range(1, pages + 1, 1):
	    if int(qitanid):
		url = IqiyiComments.COMMENTS_URL1.format(pageno=page, pagesize=IqiyiComments.DEFAULT_PAGE_SIZE, qitanid=qitanid, tvid=tvid)
	    else:
		url = IqiyiComments.COMMENTS_URL2.format(pageno=page, pagesize=IqiyiComments.DEFAULT_PAGE_SIZE, tvid=tvid)
	    self.storeurl(url, params.originalurl, IqiyiComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/20
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        jsondata = json.loads(params.content)
        comments = []
        for comment in jsondata['data']['comments']:
            try:
                curtime = int(comment['addTime'])
                content = comment['content']
                CMTStorage.storecmt(params.originalurl, content, curtime, '')
            except:
                Logger.printexception()
            
    ##############################################################################################
    # @functions：geturlplaycount
    # @params：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Liuyonglin
    # @date：2016/12/14
    # @note：
    ##############################################################################################
    def geturlplaycount(self, params):
        tvid = params.customized['tvid']
        if not self.r.search(tvid,params.content):
            Logger.log(params.url, constant.ERRORCODE_WARNNING_OTHERS)
            return
        playcount = self.r.getid(tvid, params.content)
        if playcount is not None:
            NewsStorage.setclicknum(params.originalurl, playcount)
              
    #def getlocalplaynum(self,content):
        #soup = BeautifulSoup(content, 'html5lib')
        #title = None
        #totalplaynum = None
        #flag = False
        #titleobj = soup.select_one('#widget-videotitle')
        #if not titleobj:
            #titleobj = soup.select_one('#widget-videoname')   
        #if titleobj:
            #title = titleobj.get_text().strip()
        #totalplaynumobj = soup.select_one('#widget-playcount')
        #if totalplaynumobj:
            #totalplaynum = self.str2num(totalplaynumobj.get_text())      
        #items_juji = soup.select('ul.juji-list > li')
        #if items_juji:
            #flag = True
            #return totalplaynum/len(items_juji)            
        #items = soup.select('ul.mod-play-list > li')
        #if not items:
            #items = soup.select('ul.playListScroll > li')
        #for item in items:
            #right = item.select_one('.con-right')
            #if not right:
                #continue            
            #childtitle = right.select_one('h3 > a').get('title').strip().lstrip(u'：')
            #playnum = right.select_one('p > span').get_text()
            #Logger.getlogging().debug(childtitle)
            #Logger.getlogging().debug(playnum)          
            #playnum = self.str2num(playnum)
            #if title == childtitle:
                #flag = True
                #return playnum    
        #if not flag:
            #return totalplaynum        
        
        

