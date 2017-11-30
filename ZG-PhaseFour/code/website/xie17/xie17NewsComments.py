# encoding=utf8

##############################################################################################
# @file：xie17NewsComments.py
# @author：Liyanrui
# @date：2016/12/09
# @version：Ver0.0.0.100
# @note：一起写网新闻页获取评论的文件
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility
import math
from utility.gettimeutil import getuniformtime
from utility.timeutility import TimeUtility

##############################################################################################
# @class：xie17NewsComments
# @author：Liyanrui
# @date：2016/12/09
# @note：一起写网新闻页获取评论的类，继承于WebSite类
##############################################################################################
class Xie17NewsComments(SiteComments):
    COMMENT_URL ='http://xiaoshuo.17xie.com/bookdebate.php?bid=%s&page=%d'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/12/09
    # @note：一起写网新闻页类的构造器，初始化内部变量
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
    # @date：2016/12/09
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is Xie17NewsComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                articleId = self.r.parse('^http://xiaoshuo\.17xie\.com/book/(\d+)/', params.originalurl)[0]

                # 取得评论的url列表
                comments_url = Xie17NewsComments.COMMENT_URL % (articleId, 1)
                self.storeurl(comments_url, params.originalurl, Xie17NewsComments.STEP_2, {'articleId': articleId})

            elif params.step == Xie17NewsComments.STEP_2:
                # 获得评论参数
                articleId = params.customized['articleId']

                # 取得总件数
                comment_count = float(self.r.parse(ur'共(\d+)人说过', params.content)[0])
                if comment_count == 0:
                    return

                # 判断增量
                cmtnum = URLStorage.getcmtnum(params.originalurl)
                if cmtnum >= comment_count:
                    return
                URLStorage.setcmtnum(params.originalurl, comment_count)

                # 获取页数
                page = int(math.ceil(comment_count / Xie17NewsComments.PAGE_SIZE))

                # 获得url列表
                for page in range(1, page + 1, 1):
                    url = Xie17NewsComments.COMMENT_URL % (articleId, page)
                    self.storeurl(url, params.originalurl, Xie17NewsComments.STEP_3)

            elif params.step == Xie17NewsComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                xparser = XPathUtility(params.content)
                # 取得所有评论
                comments = xparser.getcomments('/html/body/ul/li[2]/dl/dd')
                # 取得所有评论时间
                commenttimes = xparser.xpath('/html/body/ul/li[2]/dl/dt/text()')

                commentsInfo = []
                # 取得所有评论
                for index in range(0, int(len(commenttimes)), 1):
                    # 提取时间
                    if self.r.search(ur'\d+年\d+月',commenttimes[index].strip()):
                        tm = TimeUtility.getuniformtime(str(commenttimes[index]).strip(), '%Y年%m月')
                    else:
                        tm = getuniformtime(commenttimes[index].strip())

                    if URLStorage.storeupdatetime(params.originalurl, tm):
                        cmti = CommentInfo()
                        comment = comments[index * 3] + comments[index * 3 + 1] + comments[index * 3 + 2]
                        cmti.content = comment
                        commentsInfo.append(cmti)

                    # 保存获取的评论
                if len(commentsInfo) > 0:
                    self.commentstorage.store(params.originalurl, commentsInfo)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except Exception,e:
            traceback.print_exc()