# encoding=utf-8
##############################################################################################
# @file：bookComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：世纪小说网-网游小说获取评论的文件
###############################################################################################
import re
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from lxml import etree
import traceback
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility

##############################################################################################
# @class：bookComments
# @author：Liyanrui
# @date：2016/11/18
# @note：世纪小说网-网游小说获取评论的类，继承于SiteComments类
##############################################################################################
class bookComments(SiteComments):
    COMMENTS_URL = 'http://www.2200book.com/modules/article/reviews.php?aid=%s&type=all&page=%d'
    COMMENTS_URL_RID = 'http://www.2200book.com/modules/article/reviewshow.php?rid=%s'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：世纪小说网-网游小说类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3：获取评论的所有url
    #          Step4: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取评论的每一页url，并传递给共通模块
    #        Step4：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is bookComments.STEP_1:
                # 取得url中的id
                articleId = self.r.parse(r'^http://www\.2200book\.com/files/article/\w+/\d+/(\d+)\.htm$', proparam.originalurl).__getitem__(0)
                # 取得评论首页
                url = bookComments.COMMENTS_URL % (articleId, 1)
                self.storeurl(url, proparam.originalurl, bookComments.STEP_2,{'articleId': articleId})

            elif proparam.step == bookComments.STEP_2:
                articleId = proparam.customized['articleId']
                # 取得评论页数
                xparser = XPathUtility(proparam.content)
                page_count = int(self.r.parse(ur'>>(\d+)', xparser.getcomments("//*[@id='pagelink']")[0])[0])

                # 取得评论的页数
                if int(page_count) == 0:
                    return

                # 取得评论的url
                for page in range(1, int(page_count) + 1, 1):
                    url = bookComments.COMMENTS_URL % (articleId, page)
                    self.storeurl(url, proparam.originalurl, bookComments.STEP_3)

            elif proparam.step == bookComments.STEP_3:
                rids = re.findall(r'rid=(\d+)">', proparam.content)
                for rid in rids:
                    url = bookComments.COMMENTS_URL_RID % (rid)
                    self.storeurl(url, proparam.originalurl, bookComments.STEP_4)

            elif proparam.step == bookComments.STEP_4:
                commentsInfo = []
                # 论坛
                xparser = XPathUtility(proparam.content)
                comments = xparser.getcomments('//*[@id="sp_2"]/p[2]|//*[@id="b_v_5"]')
                commentTimes = self.r.parse(ur'发表于(:| )?(.+)(</p>|</div>)', proparam.content)

                for index in range(0, int(len(comments)), 1):
                    if URLStorage.storeupdatetime(proparam.originalurl, commentTimes[index][1]):
                        cmti = CommentInfo()
                        cmti.content = comments[index]
                        commentsInfo.append(cmti)

                # 保存获取的评论
                if len(commentsInfo) > 0:
                    self.commentstorage.store(proparam.originalurl, commentsInfo)

            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)

        except Exception, e:
            traceback.print_exc()