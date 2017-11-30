# encoding=utf-8
##############################################################################################
# @file：PcautoComments.py
# @author：Ninghz
# @date：2016/11/18
# @note：太平洋汽车网获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql

##############################################################################################
import json
import datetime
import traceback
import math

from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from log.spiderlog import Logger

##############################################################################################
# @class：PcautoComments
# @author：Ninghz
# @date：2016/11/18
# @note：太平洋汽车网站获取评论的类，继承于SiteComments类
##############################################################################################

class PcautoComments(SiteComments):
    COMMENTS_URL = 'http://cmt.pcauto.com.cn/action/comment/list_new_json.jsp?urlHandle=1&url=%s&pageNo=%d&pageSize=%d'
    PAGE_SIZE = 50.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3


    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/11/16
    # @note：Step1：通过共通模块传入的url，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is None:
                # 拼接第一页评论url
                comments_url = PcautoComments.COMMENTS_URL % (params.originalurl, 1, PcautoComments.PAGE_SIZE)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, PcautoComments.STEP_2)

            #获取第一页评论内容，循环获取全部评论url
            elif params.step == PcautoComments.STEP_2:
                # 获取评论的Jason返回值
                comments = json.loads(params.content)
                # 获取评论页数
                comments_count = int(comments['total'])
                NewsStorage.setcmtnum(params.originalurl, comments_count)
                if comments_count == 0:
                    return
                # 判断增量
                cmtnum = CMTStorage.getcount(params.originalurl, True)
                if cmtnum >= comments_count:
                    return
                page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages
                # 循环拼接评论url，提交下载平台获取评论数据
                for page in range(1, page_num + 1, 1):
                    commentUrl = PcautoComments.COMMENTS_URL % (params.originalurl, page, PcautoComments.PAGE_SIZE)
                    self.storeurl(commentUrl, params.originalurl, PcautoComments.STEP_3)

            #解析评论数据
            elif params.step == PcautoComments.STEP_3:
                commentsinfo = json.loads(params.content)
                comments = []
                for comment in commentsinfo['data']:
                    updatetime = comment['createTime']
                    content = comment['content']
                    curtime = TimeUtility.getuniformtime(updatetime)
                    try:
                        nick = comment['nickName']
                    except:
                        nick = 'anonymous'

                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                #     if URLStorage.storeupdatetime(params.originalurl, updatetime):
                #         cmti = CommentInfo()
                #         cmti.content = comment['content']
                #         comments.append(cmti)
                # if len(comments) > 0:
                #     self.commentstorage.store(params.originalurl, comments)

        except Exception, e:
            traceback.print_exc()