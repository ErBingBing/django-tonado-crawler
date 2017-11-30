# encoding=utf-8
##############################################################################################
# @file：xinhuaBbsComments.py
# @author：QW_Liang
# @date：2017/09/16
# @version：Ver0.0.0.100
# @note：新华网获取评论的文件
###############################################################################################
import traceback
import re
import time

from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：xinhuaBbsComments
# @author：QW_Liang
# @date：2017/09/16
# @note：新华网获取评论的类，继承于SiteComments类
##############################################################################################
class xinhuaBbsComments(SiteComments):
    COMMENTS_URL = 'http://forum.home.news.cn/detail/%s/%d.html'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    PAGE_SIZE = 20
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：新华网类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is xinhuaBbsComments.STEP_1:
                # 取得url中的id
                articleId = re.findall(r'^http://forum\.home\.news\.cn/\w+/(\d+)/\d+\.html',proparam.originalurl).__getitem__(0)
                # 取得评论的url列表
                comments_url = xinhuaBbsComments.COMMENTS_URL % (articleId, 1)
                self.storeurl(comments_url, proparam.originalurl, xinhuaBbsComments.STEP_2, {'articleId': articleId})

            elif proparam.step == xinhuaBbsComments.STEP_2:
                articleId = proparam.customized['articleId']
                xparser = XPathUtility(proparam.content)
                pages = xparser.getcomments('//*[@id="postreply"]/div[2]/ul[1]/li/a')
                comments = xparser.getcomments('//*[@id="postreply"]/dl/dd/div/p[2]')
                comments_count = len(comments)
                # 如果页数为0
                if len(pages) == 0 and comments_count != 0:
                    url = xinhuaBbsComments.COMMENTS_URL % (articleId, 1)
                    self.storeurl(url, proparam.originalurl, xinhuaBbsComments.STEP_3)

                # 增量判断
                cmtnum = CMTStorage.getcount(proparam.originalurl,True)
                if cmtnum >= comments_count:
                    return

                page_num = int(len(pages))
                # 判断页数
                if page_num >= self.maxpages:
                    page_num = self.maxpages

                start = int(cmtnum / self.PAGE_SIZE) + 1
                end = int(page_num)
                if end > start + self.maxpages:
                    start = end - self.maxpages

                # 循环取得评论的url
                for page_num in range(end, start - 1, -1):
                    # 取得评论的url
                    url = xinhuaBbsComments.COMMENTS_URL % (articleId, page_num)
                    self.storeurl(url, proparam.originalurl, xinhuaBbsComments.STEP_3)

            elif proparam.step == xinhuaBbsComments.STEP_3:
                # 取得评论
                xparser = XPathUtility(proparam.content)
                comments = xparser.getcomments('//*[@id="postreply"]/dl/dd/div/p[2]')
                cmtnum = CMTStorage.getcount(proparam.originalurl, True)
                comments_count = len(comments)
                NewsStorage.setcmtnum(proparam.originalurl, comments_count + cmtnum)
                # 评论存在的场合
                if len(comments) != 0:
                    # 取得发布时间
                    publicTimes = re.findall(ur'<li><span id="time_\d+">(\d+-\d+-\d+ \d+:\d+:\d+)发表</span></li>', proparam.content)
                    publicIndex = 0
                    nicks = xparser.getcomments('//*[@id="postreply"]/dl/dd/ul[1]/li[1][a]')
                    for comment in comments:
                        content = comment
                        publictime = publicTimes[publicIndex]
                        curtime = TimeUtility.getuniformtime(publictime)
                        nick = nicks[publicIndex]

                        if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
                        publicIndex = publicIndex + 1

            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)

        except Exception, e:
            traceback.print_exc()



