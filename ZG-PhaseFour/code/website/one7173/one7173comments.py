# encoding=utf-8
##############################################################################################
# @file：oneSevenOneSevenThree.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：17173视频页获取评论的文件
###############################################################################################
import re
import json
import math
from log.spiderlog import Logger
from configuration import constant
from utility.bbs2commom import CommenComments
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
##############################################################################################
# @class：oneSevenOneSevenThree
# @author：Liang
# @date：2017/08/24
# @note：17173视频页获取评论的类，继承于SiteComments类
##############################################################################################
class One7173Comments(SiteComments):

    CLICK_URL = 'http://v.17173.com/japi/video/getPlayCount?ids={vid}'
    COMMENT_URL = 'http://comment2.17173.com/front/comment/list.do?sid={sid}&pageSize={page_size}&pageNo={page}&sort=1'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_CLICK = 4
    page_size = 20

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liang
    # @date：2017/08/24
    # @note：17173视频页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.changyan = None
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：
    # @author：Liang
    # @date：2017/08/24
    # @note：Step1：
    ##############################################################################################
    #----------------------------------------------------------------------
    def process(self, params):
        if self.r.search('https?://bbs\.17173\.com/.*', params.originalurl):
            CommenComments(self).process(params)
        else:
            self.process_news(params)
    #----------------------------------------------------------------------
    def process_news(self, params):
        try:
            if params.step == None:
                self.step1(params)
                if self.r.search('https?://v\.17173\.com/.*', params.originalurl):
                    self.get_clickurl(params)                
            elif params.step == self.STEP_2:
                self.step2(params)            
            elif params.step == self.STEP_3:
                self.step3(params)
            elif params.step == self.STEP_CLICK:
                self.set_click(params)
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self, params):
        sid= self.r.getid('article.infoCommentHref', params.content, split='=')
        if not sid:
            sid= self.r.getid('data-widget-sid', params.content, split='=')
        url = self.COMMENT_URL.format(page_size=self.page_size, sid=sid, page=1)                      
        self.storeurl(url, params.originalurl, self.STEP_2, {'sid':sid})
    #----------------------------------------------------------------------
    def step2(self, params):
        sid = params.customized['sid']
        jsondata = json.loads(params.content)
        curcmtnum = jsondata['data']['totalCount']
        NewsStorage.setcmtnum(params.originalurl, curcmtnum)
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        if dbcmtnum >= curcmtnum:
            return
        page_num=int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        for page in range(1,page_num+1):
            if page == 1:
                self.step3(params)
                continue
            url = self.COMMENT_URL.format(page_size=self.page_size, page=page, sid=sid)
            self.storeurl(url, params.originalurl, self.STEP_3)

    #----------------------------------------------------------------------
    def step3(self, params):
        jsondata = json.loads(params.content)
        comments = jsondata['data']['listData']
        for comment in comments:
            try:
                content = comment['content']
                curtime = comment['createTime']
                CMTStorage.storecmt(params.originalurl, content, curtime, '')  
            except:
                Logger.printexception()

    # http://v.17173.com/japi/video/getPlayCount?ids=%2C810729
    # 获取到videoid，插入ids=%2C后
    def get_clickurl(self,params):
        vid = self.r.getid('videoId', params.content)
        clickurl = One7173Comments.CLICK_URL.format(vid=vid)
        self.storeurl(clickurl, params.originalurl, One7173Comments.STEP_CLICK,{'vid':vid})

    def set_click(self,params):
        try:
            vid = params.customized['vid']
            data = json.loads(params.content)
            clicknum = data['data'][vid]
            NewsStorage.setclicknum(params.originalurl, clicknum)
        except:
            Logger.printexception()