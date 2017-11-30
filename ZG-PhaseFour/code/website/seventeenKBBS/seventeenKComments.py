# encoding=utf8

##############################################################################################
# @file：shanbacomments.py
# @author：HuBorui
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：凤凰视频获取评论的文件
##############################################################################################

import json
import math
import datetime
import traceback

from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from storage.urlsstorage import URLCommentInfo

##############################################################################################
# @class：fenghuangComments
# @author：HuBorui
# @date：2016/11/20
# @note：凤凰视频获取评论的类，继承于WebSite类
##############################################################################################
class SeventeenKComments(SiteComments):
    COMMENT_URL ='http://bbs.17k.com/thread-{docurl}-{page}-1.html'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/20
    # @note：fenghuangComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)


    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：HuBorui
    # @date：2016/11/20
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is SeventeenKComments.STEP_1:
                 #Step1: 通过得到docurl，得到获取评论的首页url。
                 #Logger.getlogging().info("proparam.step is None")
                 # 在视频url中取出docurl，^http://v\.ifeng\.com\/\w+\/\w+/\d{6}\/[0-9a-z-]+\.shtml
                 # 取URL中的([0-9a-z-]+)参数，此参数为docurl
                 docurl = self.r.parse('^http://bbs\.17k\.com\/thread-(\d+)-\d+-1\.html',params.originalurl)[0]
                 #Logger.getlogging().debug(docurl)
                 # 评论首页URL为http://comment.ifeng.com/getv.php?job=1&docurl=([0-9a-z-]+)&p=1
                 commentinfo_url = 'http://bbs.17k.com/thread-{docurl}-1-1.html'.format(docurl = docurl)
                 self.storeurl(commentinfo_url, params.originalurl, SeventeenKComments.STEP_2,{'docurl': docurl})

            elif params.step == SeventeenKComments.STEP_2:
                 #将STEP_1中的docurl传下来
                 docurl = params.customized['docurl']
                 # Step2: 通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
                 #Logger.getlogging().info("params.step == 2")
                 # 打开STEP1中URL，截取"count"：num字段，取出num的值，num字段为评论总数
                 xparser = XPathUtility(params.content)
                 commentsinfo = xparser.getnumber('//*[@class="hm ptn"]/span[5]')

                 #Logger.getlogging().debug(comments_count / self.page_size)
                 #Logger.getlogging().debug(math.ceil(comments_count / self.page_size))

                 # 保存页面评论量
                 cmtnum = URLStorage.getcmtnum(params.originalurl)
                 if cmtnum >= int(commentsinfo):
                     return
                 URLStorage.setcmtnum(params.originalurl, int(commentsinfo))

                 # 总数除以page_size，然后加1，可得到评论总页数comments_count
                 # 循环http://comment.ifeng.com/getv.php?job=1&docurl=([0-9a-z-]+)&p=comments_count，从一开始循环到上一步操作取到的数值，从而得到所有评论的URL,并保存
                 pagecount = xparser.getnumber('//*[@class="pg"]/label/span')

                 for page in range(1, pagecount+1, 1):
                     comment_url =  SeventeenKComments.COMMENT_URL.format(docurl =docurl,page=page)
                     self.storeurl(comment_url, params.originalurl, SeventeenKComments.STEP_3,{'page': page})

            elif params.step == SeventeenKComments.STEP_3:
                 # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                 #Logger.getlogging().info("params.step == 3")
                 page = params.customized['page']
                 xparser = XPathUtility(params.content)
                 commentsinfo = xparser.getcomments('//*[contains(@id,"postmessage")]')
                 commentstime = self.r.parse(ur'发表于 (\d+-\d+-\d+ \d+:\d+)</em>', params.content)
                 comments = []

                 #获取评论
                 # 设置实际的评论量
                 if page is 1:
                     statrIndex =1
                 else:
                     statrIndex = 0
                 for index in range(statrIndex,len(commentstime),1 ):
                     cmti = CommentInfo()
                     if URLStorage.storeupdatetime(params.originalurl,commentstime[index]+':00'):
                         # 获取增加的评论（根据时间比较）
                         cmti.content = commentsinfo[index]
                         comments.append(cmti)
                 # 保存获取到的评论
                 if len(comments) > 0:
                     self.commentstorage.store(params.originalurl, comments)

            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))

        except Exception,e:
            traceback.print_exc()

