# encoding=utf-8
##############################################################################################
# @file：AllComments.py
# @author：Merlin.W.OUYANG
# @date：2016/12/6
# @note：评论获取
##############################################################################################

import json
import math
import urllib
from bsddb import db
import math
from utility.httputil import HttpUtility
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
import traceback
from utility.gettimeutil import getuniformtime

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/12/6
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    COMMENTS_URL = 'http://api.v2.uyan.cc/v4/action/?sid=%s&pn=%s'
    SID_URL = 'http://api.v2.uyan.cc/v4/comment/?uid=413&url=%s'
    PAGE_SIZE = 3
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/12/6
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        #----------------------------------------------------------------------
        ##############################################################################################
        # @functions：process
        # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
        # @return：Step1：获取评论的首页url
        #          Step2：获取评论的所有url
        #          Step3: 抽出的评论和最新评论的创建时间
        # @author：Merlin.W.ouyang
        # @date：2016/12/6
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
        #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
        #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
        #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
        #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
        ##############################################################################################   

    def process(self, params):
        try:
            if params.step is AllComments.STEP_1:
                comments_url = AllComments.SID_URL % (params.originalurl)
                self.storeurl(comments_url, params.originalurl, AllComments.STEP_2)

            elif params.step is AllComments.STEP_2:
                try:
                    threadid = self.r.parse('"sid":(.*?),"',params.content)[0]
                    curcmtnum=int(self.r.parse('"postcount":(.*?),"', params.content)[0])
                    NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
                    dbcmtnum = CMTStorage.getcount(params.originalurl, True)
                    if dbcmtnum >= curcmtnum:
                        return
                    pagenum = int(math.ceil(float(curcmtnum-dbcmtnum)/3))
                    for page in range(0, pagenum, 1):
                        comments_url = AllComments.COMMENTS_URL % (threadid, page)
                        self.storeurl(comments_url, params.originalurl, AllComments.STEP_3)
                except:
                    Logger.printexception()

            elif params.step is AllComments.STEP_3:
                # 获取评论的Jason返回值
                commentsinfo = json.loads(params.content)
                comments = []
                for comment in commentsinfo['data']:
                    pubdate = getuniformtime(comment['time'])
                    content = comment['cnt']
                    CMTStorage.storecmt(params.originalurl, content, pubdate, '')
        except:
            Logger.printexception()