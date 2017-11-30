# coding=utf-8
##############################################################################################
# @file：funcomments.py
# @author：Ninghz
# @date：2016/11/20
# @note：风行视频网站获取评论的文件
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

##############################################################################################
# @class：FunComments
# @author：Ninghz
# @date：2016/11/20
# @note：风行视频网站获取评论的类，继承于SiteComments类
##############################################################################################
class FunComments(SiteComments):
    COMMENTS_URL = 'http://api1.fun.tv/comment/display/gallery/%s?pg=%d'
    PAGE_SIZE = 30
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/11/20
    # @note：FuntvComments类的构造器，初始化内部变量
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
    # @date：2016/11/20
    # @note：Step1：通过共通模块传入的html内容获取到galleryid，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                # 从url中获取拼接评论url的参数
                if not self.r.search('^http[s]{0,1}://www\.fun\.tv/vplay/\w-(\d+)(\.\w-\d+)?/$', params.originalurl):
                    return
                galleryid = self.r.parse('^http[s]{0,1}://www\.fun\.tv/vplay/\w-(\d+)(\.\w-\d+)?/$', params.originalurl)[0][0]
                # 拼接第一页评论url
                comments_url = FunComments.COMMENTS_URL % (galleryid, 1)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, FunComments.STEP_2, {'galleryid': galleryid})
                
                #直接通过拼页面获取，除电视剧存在此种合辑问题，其他都可以直接获取
                xhtml = XPathUtility(params.content)
                torrent_panel=xhtml.xpath('//*[@class="torrent-panel"]')
                if torrent_panel:
                    lis = xhtml.xpath('//*[@class="torrent-panel"]/ul/li')
                    if len(lis) == 0:
                        return
                    numobj = xhtml.xpath('//*[@class="playInfo crumbs"]/div/a[@class="exp-num"]')
                    if numobj:
                        clicknum = self.str2num(numobj[0].text)
                        new_clicknum = int(clicknum)/len(lis)
                        NewsStorage.setclicknum(params.originalurl, new_clicknum)

            #获取第一页评论内容，循环获取全部评论url
            elif params.step == FunComments.STEP_2:
                galleryid = params.customized['galleryid']
                # 获取评论的Jason返回值
                comments = json.loads(params.content)
                # 比较上次抓取该url的页面评论量和当前取到的评论量
                curcmtnum = int(comments['data']['total_num'])
		NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
		dbcmtnum = CMTStorage.getcount(params.originalurl, True)
		if dbcmtnum >= curcmtnum:
		    return    
		# 循环取得评论的url
		pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.PAGE_SIZE))
		if pages >= self.maxpages:
		    pages = self.maxpages
                for page in range(1,  pages+1, 1):
                    if page == 1:
                        self.step3(params)
                        continue
                    commentUrl = FunComments.COMMENTS_URL % (galleryid, page)
                    self.storeurl(commentUrl, params.originalurl, FunComments.STEP_3, {'galleryid': galleryid})
            #解析评论数据
            elif params.step == FunComments.STEP_3:
                self.step3(params)
        except:
            Logger.printexception()
            
    def step3(self,params):
        commentsinfo = json.loads(params.content)
        for comment in commentsinfo['data']['comment']:
            try:
                curtime = comment['time']
                content = comment['content']
                CMTStorage.storecmt(params.originalurl, content, curtime, '')
            except:
                Logger.printexception()
            
       
