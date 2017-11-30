# encoding=utf-8
##############################################################################################
# @file：rayliComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：瑞丽网获取评论的文件
###############################################################################################
import math
import re
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from log.spiderlog import Logger
from lxml import etree
from bs4 import BeautifulSoup
import traceback

##############################################################################################
# @class：rayliComments
# @author：Liyanrui
# @date：2016/11/18
# @note：瑞丽网获取评论的类，继承于SiteComments类
##############################################################################################
class rayliComments(SiteComments):
    COMMENTS_URL = 'http://bbs.rayli.com.cn/forum-viewthread-tid-%s-extra-page=1-page-%d.html'
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
    # @note：瑞丽网类的构造器，初始化内部变量
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
            if proparam.step is rayliComments.STEP_1:
                # 取得html中的commentType
                articleId = re.findall('^http://bbs\.rayli\.com\.cn/gallery-(\d+)-\d+.html', proparam.url).__getitem__(0)

                #取得评论url
                comments_url = rayliComments.COMMENTS_URL % (articleId, 1)
                self.storeurl(comments_url, proparam.originalurl, rayliComments.STEP_2, {'articleId': articleId,})

            elif proparam.step == rayliComments.STEP_2:
                articleId = proparam.customized['articleId']
                # 取得评论个数
                comments_count = float(re.findall(ur'回复:</span> (\d+)</div>', proparam.content).__getitem__(0))
                if int(comments_count) == 0:
                    return

                # 判断增量
                cmtnum = CMTStorage.getcount(proparam.originalurl, True)
                if cmtnum >= comments_count:
                    return
                NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages

                # 循环取得评论的url
                for page in range(1, page_num + 1, 1):
                    # 取得评论的url
                    url = rayliComments.COMMENTS_URL % (articleId, page)
                    self.storeurl(url, proparam.originalurl, rayliComments.STEP_3)

            elif proparam.step == rayliComments.STEP_3:
                commentsInfo = []
                soup = BeautifulSoup(proparam.content, 'html.parser')
                # 获取评论
                comments = soup.select('.t_f')
                # 获取评论时间
                commentTime = self.r.parse(ur'<em id="authorposton\d+">发表于 (.+?)</em>', proparam.content)
                # 获取nick
                nicks = soup.select('.xw1')

                # 是否首页
                page = int(self.r.parse(ur'page=1-page-(\d+)', proparam.url)[0])
                if page == 1:
                    index = 1
                else:
                    index = 0
                publishlist = [TimeUtility.getcurrentdate(TimeUtility.DEFAULTFORMAT)]
                if len(comments) >0:
                    # 获取评论
                    for index in range(index, len(comments), 1):
                        content = comments[index].text.strip()
                        curtime = commentTime[index]
                        nick = nicks[index].text
                        publishlist.append(curtime)
                        if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
                        # cmti = CommentInfo()
                        # if URLStorage.storeupdatetime(proparam.originalurl, commentTime[index]):
                        #    cmti.content = comments[index].text
                        #    commentsInfo.append(cmti)
                if len(publishlist) > 0:
                    publishdate = min(publishlist)
                    NewsStorage.setpublishdate(proparam.originalurl,publishdate)


                # # 保存获取的评论
                # if len(commentsInfo) > 0:
                #     self.commentstorage.store(proparam.originalurl, commentsInfo)
            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)

        except Exception, e:
            traceback.print_exc()