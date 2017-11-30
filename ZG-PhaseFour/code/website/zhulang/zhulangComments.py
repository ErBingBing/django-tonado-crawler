# encoding=utf8

##############################################################################################
# @file：zhulangComments.py
# @author：Liyanrui
# @date：2016/12/06
# @version：Ver0.0.0.100
# @note：逐浪文学网-网游小说新闻页获取评论的文件
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
import math
import json

##############################################################################################
# @class：zhulangComments
# @author：Liyanrui
# @date：2016/12/06
# @note：逐浪文学网-网游小说新闻页获取评论的类，继承于WebSite类
##############################################################################################
class zhulangComments(SiteComments):
    COMMENT_URL ='http://www.zhulang.com/ajax/comment/getBookAllComment/bk_id/%s/sessionid/1.html?p=%d'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/12/06
    # @note：逐浪文学网-网游小说新闻页类的构造器，初始化内部变量
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
    # @date：2016/12/06
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is zhulangComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                articleId = self.r.parse('http://www.zhulang.com/(\d+)/', params.originalurl)[0]

                # 取得评论的url列表
                comments_url = zhulangComments.COMMENT_URL % (articleId, 1)
                self.storeurl(comments_url, params.originalurl, zhulangComments.STEP_2, {'articleId': articleId})

            elif params.step == zhulangComments.STEP_2:
                # 获得评论参数
                articleId = params.customized['articleId']

                # 取得总件数
                comment_count = float(self.r.getid('total', params.content))
                if comment_count == 0:
                    return

                # 判断增量
                cmtnum = URLStorage.getcmtnum(params.originalurl)
                if cmtnum >= comment_count:
                    return
                URLStorage.setcmtnum(params.originalurl, comment_count)

                # 获取页数
                page = int(math.ceil(comment_count / zhulangComments.PAGE_SIZE))

                # 获得url列表
                for page in range(0, page, 1):
                    url = zhulangComments.COMMENT_URL % (articleId, page)
                    self.storeurl(url, params.originalurl, zhulangComments.STEP_3)

            elif params.step == zhulangComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                # 取得所有评论
                comments = self.r.parse(r'<p class=\\"cmt-txt\\">(.+?)<\\/p>', params.content)

                # 取得所有评论时间
                commenttimes = self.r.parse(r'<span class=\\"cmt-time\\">(.+?)<\\/span>', params.content)

                index = 0
                commentsInfo = []
                # 取得所有评论
                for index in range(index, int(len(comments)), 1):
                    # 提取时间
                    publicTime = commenttimes[index]
                    if URLStorage.storeupdatetime(params.originalurl, publicTime):
                        cmti = CommentInfo()
                        x = json.loads('{"comment":"%s"}' % comments[index].encode('utf8'))
                        cmti.content = (x['comment'])
                        commentsInfo.append(cmti)

                    # 保存获取的评论
                if len(commentsInfo) > 0:
                    self.commentstorage.store(params.originalurl, commentsInfo)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except Exception,e:
            traceback.print_exc()