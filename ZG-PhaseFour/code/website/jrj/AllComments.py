# encoding=utf-8
##############################################################################################
# @file：pcgamescomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/18
# @note：金融界评论获取
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################################################

import json
import math
import urllib
from bsddb import db
from utility.httputil import HttpUtility
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
# from storage.commentsstorage import CommentInfo
# from storage.urlsstorage import URLStorage
from log.spiderlog import Logger
import traceback
import time
import datetime
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/11/18
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    COMMENTS_URL = "http://news.comments.jrj.com.cn/index.php/commentslist?appId=%s&appItemid=%s&pageSize=50&page=%d"
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    
        ##############################################################################################
        # @functions：__init__
        # @param： none
        # @return：none
        # @author：Merlin.W.OUYANG
        # @date：2016/11/18
        # @note：AllComments类的构造器，初始化内部变量
        ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        #self.r = RegexUtility()
        #self.basicstorage = BaseInfoStorage()
        #self.commentstorage = CommentsStorage()
    
    #----------------------------------------------------------------------
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
    def  process (self, params):
        try:
            if params.step is AllComments.STEP_1:
                appID = self.r.parse("appId='(.+?)';",params.content)[0];
                appItemid = self.r.parse("appItemid=(.+?);",params.content)[0];
                comments_url = AllComments.COMMENTS_URL % (appID, appItemid, 1)
                self.storeurl(comments_url, params.originalurl, AllComments.STEP_2, {'key':appID, 'appItemid':appItemid,'pageno':1}) 
                
            elif params.step is AllComments.STEP_2:
                appID = params.customized['key']
                appItemid = params.customized['appItemid']
                comments = json.loads(params.content)
                page_count = int(comments['totalPage'])
                comments_url = AllComments.COMMENTS_URL % (params.customized['key'], params.customized['appItemid'], params.customized['pageno'])
                self.storeurl(comments_url, params.originalurl, AllComments.STEP_3, 
                              {'key':params.customized['key'], 
                               'appItemid':params.customized['appItemid'],
                               'pageno':params.customized['pageno'],
                               'totalpage':page_count})
                comments_count = float(comments['totalCount'])
                NewsStorage.setcmtnum(params.originalurl, int(comments_count))
                # 判断增量
                cmtnum = CMTStorage.getcount(params.originalurl, True)
                if cmtnum >= comments_count:
                    return
                page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages
                for page in range(1, page_num + 1,1):
                    comments_url = AllComments.COMMENTS_URL % (
                        appID, appItemid, page)
                    self.storeurl(comments_url, params.originalurl, AllComments.STEP_3,
                                  {'key': params.customized['key'],
                                   'appItemid': params.customized['appItemid'],
                                   'pageno': params.customized['pageno'],
                                   'totalpage': page_count})
                
            elif params.step is AllComments.STEP_3:
                comments = json.loads(params.content)
                roll = len(comments['listData'])
                ptime = []
                pcontent = []
                nicks = []
                ctime=0
                if params.customized['pageno'] <= params.customized['totalpage']:
                    while ctime < roll:
                        ptimer= time.localtime(comments['listData'][ctime][-1]['ctime'])
                        ptimer= TimeUtility.getuniformtime(time.strftime('%Y-%m-%d %H:%M:%S',ptimer))
                        # ptimer = TimeUtility.getuniformtime(ptimer)
                        pcontent.append(comments['listData'][ctime][-1]['content'])
                        nicks.append(comments['listData'][ctime][-1]['senderName'])
                        ptime.append(ptimer)
                        ctime =ctime +1
                    for index in range(0, int(len(pcontent)), 1):
                        content = pcontent[index]
                        curtime = str(TimeUtility.getuniformtime(ptime[index]))
                        nick = nicks[index]
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)

        except Exception, e:
            traceback.print_exc()
            Logger.getlogging().error(e.message)             

        