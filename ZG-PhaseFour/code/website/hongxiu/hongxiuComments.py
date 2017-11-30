# encoding=utf8

##############################################################################################
# @file：TaDuComments.py
# @author：Yongjicao
# @date：2016/12/09
# @version：Ver0.0.0.100
# @note：塔读文学-书库新闻页获取评论的文件
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from utility.gettimeutil import getuniformtime
import math
from bs4 import BeautifulSoup
##############################################################################################
# @class：TaDuComments
# @author：Yongjicao
# @date：2016/12/09
# @note：塔读文学-书库新闻页获取评论的类，继承于WebSite类
##############################################################################################
class HongXiuComments(SiteComments):
    COMMENT_URL ='http://pinglun.hongxiu.com/pinglun{bookId}_1_{page}.html'
    COMMENT_URL_REPLY ='http://pinglun.hongxiu.com/{replyId}.html'
    PAGE_SIZE = 25
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/12/09
    # @note：塔读文学-书库新闻页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Yongjicao
    # @date：2016/12/09
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is HongXiuComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                bookId = self.r.parse('http://\w+\.hongxiu\.com/\w+/(\d+).*', params.originalurl)[0]

                # 取得评论的url列表
                comments_url = HongXiuComments.COMMENT_URL.format (bookId =bookId,page = 1)
                self.storeurl(comments_url, params.originalurl, HongXiuComments.STEP_2, {'bookId': bookId})
            elif params.step == HongXiuComments.STEP_2:
                # 获得评论参数
                bookId = params.customized['bookId']

                # 取得总件数
                params.content = (params.content).encode('utf-8')
                comment_count = self.r.parse('strong id="htmlrecordcnt" class="total">(\d+)</strong>条', params.content)[0]
                if comment_count == 0:
                    return

                # 判断增量
                cmtnum = URLStorage.getcmtnum(params.originalurl)
                if cmtnum >= comment_count:
                    return
                URLStorage.setcmtnum(params.originalurl, comment_count)

                # 获取页数
                totalPage = int(math.ceil(float(comment_count) / HongXiuComments.PAGE_SIZE))

                # 获得url列表
                for page in range(1, totalPage+1 , 1):
                    url = HongXiuComments.COMMENT_URL.format(bookId = bookId,page = page)
                    self.storeurl(url, params.originalurl, HongXiuComments.STEP_3)

            elif params.step == HongXiuComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                # 取得所有评论
                soup = BeautifulSoup(params.content, 'html5lib')
                comments = soup.select('.inner')

                # 取得所有评论时间
                commenttimes = soup.select('.postTime')

                commentsInfo = []
                # 取得所有评论
                for index in range(0, int(len(comments)), 1):
                    # 提取时间
                    publicTime = self.r.parse(ur'(.*) 发表',commenttimes[index].get_text())[0]
                    tm = getuniformtime(publicTime)
                    if URLStorage.storeupdatetime(params.originalurl, tm):
                        cmti = CommentInfo()
                        cmti.content = self.r.parse(ur'发表([\s\S]*)', comments[index].get_text().strip())[0]
                        commentsInfo.append(cmti)
                    # 保存获取的评论
                if len(commentsInfo) > 0:
                    self.commentstorage.store(params.originalurl, commentsInfo)

            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except Exception,e:
            traceback.print_exc()