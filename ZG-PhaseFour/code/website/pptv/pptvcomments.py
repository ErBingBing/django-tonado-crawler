# encoding=utf-8
##############################################################################################
# @file：pptvcomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：PPTV动漫评论获取
##############################################################################################

import json
import re
import math
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from configuration import constant 
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage 
##############################################################################################
# @class：PptvComments
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class PptvComments(SiteComments):
    COMMENTS_URL = 'http://apicdn.sc.pptv.com/sc/v3/pplive/ref/vod_%s/feed/list?appplt=web&action=1&pn=%d&ps=20'
    COMMENTS_URL_SUM = 'http://apicdn.sc.pptv.com/sc/v3/pplive/ref/vod_%s/feed/list?appplt=web&action=1&pn=%d&ps=20'
    # 侧边栏信息接口
    PLAY_URL = 'http://apis.web.pptv.com/show/videoList?pid={pid}&cat_id={cat_id}'
    DETAIL_URL = 'http://v.pptv.com/page/{v_id}.html'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_CLICK = 4
     
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/20
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Merlin.W.ouyang
    # @date：2016/11/18
    # @note：Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
    #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
    #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
    #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
    #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
    ##############################################################################################
    def process(self, params):
        try:
            if not self.r.search('^http[s]{0,1}://v\.pptv\.com/show/\w+\.html.*', params.originalurl):
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_TEMPLATE)
                return
            if params.step is PptvComments.STEP_1:
                self.step1(params)
                self.get_clickurl(params)
            elif params.step is PptvComments.STEP_2:
                self.step2(params)
            elif params.step is PptvComments.STEP_3:
                self.step3(params)
            elif params.step == PptvComments.STEP_CLICK:
                self.setclick(params)
        except:
            Logger.printexception()

    def step1(self, params):
        if self.r.search('var\swebcfg\s=\s\{\"id\":(\d+),', params.content):
            vod = self.r.parse('var\swebcfg\s=\s\{\"id\":(\d+),', params.content)[0]
            comments_url = PptvComments.COMMENTS_URL_SUM % (vod, 0)
            self.storeurl(comments_url, params.originalurl, PptvComments.STEP_2, {'vod': vod})
        else:
            Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_OTHERS)

    def step2(self, params):
        vod = params.customized['vod']
        comments = json.loads(params.content)
        curcmtnum = int(comments['data']['total'])
        NewsStorage.setcmtnum(params.originalurl, curcmtnum)
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        if cmtnum >= curcmtnum:
            return        
        page_num=int(math.ceil((float(curcmtnum-cmtnum)/self.PAGE_SIZE)))
        if int(page_num) >= self.maxpages:
            page_num = self.maxpages
        for page in range(0,page_num+1):
            if page == 0:
                params.customized['page'] = 0
                params.customized['startpage'] = 0
                self.step3(params)
                continue
            comments_url = PptvComments.COMMENTS_URL_SUM % (vod, page)
            self.storeurl(comments_url, params.originalurl, PptvComments.STEP_3, {'page':page, 'startpage':0})

    def step3(self, params):
        page = params.customized['page']
        startpage = params.customized['startpage']
        comments = json.loads(params.content)
        commentsInfo = []
        pubdatelist = []
        for comment in comments['data']['page_list']:
            try:
                pubdate = comment['create_time']
                pubdatelist.append(pubdate)
                content = comment['content']
                CMTStorage.storecmt(params.originalurl, content, pubdate, '')
            except:
                Logger.printexception()
        if page == startpage:
            if pubdatelist:
                NewsStorage.setpublishdate(params.originalurl, max(pubdatelist))
     
    def get_clickurl(self, params):
        pattern = 'http[s]{0,1}://v\.pptv\.com/page/(\w+)\.html'
        if self.r.search(pattern, params.content):
            v_id = self.r.parse(pattern, params.content)[0]
            detailurl = PptvComments.DETAIL_URL.format(v_id=v_id)
            self.storeurl(detailurl, params.originalurl, PptvComments.STEP_CLICK)

    def setclick(self, params):
        try:
            pattern = u'<li>播放：(.*)</li>?'
            if self.r.search(pattern, params.content):
                clicknum = self.r.parse(pattern, params.content)[0]
                #clicknum = params.content.split(u'<li>播放：')[1].split('</li>')[0]
                clicknum = self.str2num(clicknum)
                NewsStorage.setclicknum(params.originalurl, clicknum)
        except:
            Logger.printexception()
