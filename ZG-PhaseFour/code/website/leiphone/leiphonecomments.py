# encoding=utf-8
##############################################################################################
# @file：leiphonecomments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：雷锋网获取评论的文件
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################
import json
import re

from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
import traceback
from bs4 import BeautifulSoup

##############################################################################################
# @class：LeiphoneComments
# @author：Liyanrui
# @date：2016/11/18
# @note：雷锋网获取评论的类，继承于SiteComments类
##############################################################################################
class LeiphoneComments(SiteComments):
    COMMENTS_URL = 'https://home.leiphone.com/comment/loadCommentJson?item_id=%s&type=2'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：界面类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is LeiphoneComments.STEP_1:
                # 取得url中的id
                articleId = self.r.getid('data-article_id', proparam.content)
                comments_url = LeiphoneComments.COMMENTS_URL % (articleId)
                self.storeurl(comments_url, proparam.originalurl, LeiphoneComments.STEP_2, {'articleId': articleId})

            elif proparam.step == LeiphoneComments.STEP_2:
                articleId = proparam.customized['articleId']
                comments = proparam.content[proparam.content.index('{'): proparam.content.rindex('}')+1]
                comments = json.loads(comments)
                comments_count = float(comments['allCount']['num'])
                NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                # 取得评论件数
                if int(comments_count) == 0:
                    return

                # 判断增量
                cmtnum = CMTStorage.getcount(proparam.originalurl,True)
                if cmtnum >= comments_count:
                    return


                # 取得评论
                self.geturlcomments(proparam)

                # 取得评论url
                # comments_url = LeiphoneComments.COMMENTS_URL % (articleId)
                # self.storeurl(comments_url, proparam.originalurl, LeiphoneComments.STEP_3)

            elif proparam.step == LeiphoneComments.STEP_3:
                return
                # # 取得评论的正则表达式
                # comments = re.findall(r'content":"(.+?)","paragraph_id"', proparam.content)
                # commentsInfo = []
                # commentsTime = self.r.parse(r'origin_created":"(\d+)","member_avatarPath"', proparam.content)
                # # 取得评论
                # index = 0
                # for comment in comments:
                #     comment = eval('u"' + comment + '"')
                #     cmti = CommentInfo()
                #     cmti.content = comment.encode('utf-8')
                #     if URLStorage.storeupdatetime(proparam.originalurl, getuniformtime(commentsTime[index])):
                #         commentsInfo.append(cmti)
                #     index = index + 1
                #
                # # 保存获取的评论
                # if len(commentsInfo) > 0:
                #     self.commentstorage.store(proparam.originalurl, commentsInfo)
            else:
                return

        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：geturlcomments
    # @proparam： 共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：none
    # @author：Hedian
    # @date：2016/12/27
    # @note：Step3没有必要做，把Step3的代码抽出为该方法
    ##############################################################################################
    def geturlcomments(self, proparam):
        # soup = BeautifulSoup(proparam.content, 'html5lib')
        # lis = soup.select('.comment-say')
        # for li in lis:
        #     content = li.select_one('.des').get_text()
        #     curtime = li.select_one('.time').get_text()
        #     nick = li.select_one('.name replyName').get_text()
        #     if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
        #         CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
        # 取得评论的正则表达式
        comments = re.findall(r'content":"(.+?)","paragraph_id"', proparam.content)
        commentsTime = self.r.parse(r'origin_created":"(\d+)","member_avatarPath"', proparam.content)
        nicks = self.r.parse(r'"nickname":"(.*?)","is_hot"', proparam.content)
        # 取得评论
        index = 0
        for comment in comments:
            comment = eval('u"' + comment + '"')
            content = comment.encode('utf-8')
            curtime = TimeUtility.getuniformtime(commentsTime[index])
            nick = eval('u"' + nicks[index] + '"')
            nick = nick.encode('utf-8')
            if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
            index = index + 1

