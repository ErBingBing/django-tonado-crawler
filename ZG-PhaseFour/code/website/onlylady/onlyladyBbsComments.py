# encoding=utf8

##############################################################################################
# @file：OnlyladyComments.py
# @author：HuBorui
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：女人志获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################################################

import math
import traceback

from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from utility.gettimeutil import TimeUtility


##############################################################################################
# @class：OnlyladyComments
# @author：HuBorui
# @date：2016/11/30
# @note：女人志获取评论的类，继承于WebSite类
##############################################################################################
class OnlyladyBbsComments(SiteComments):
    COMMENT_URL ='http://bbs.onlylady.com/thread-{docurl}-{page}-1.html'
    STEP_1 = None
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/30
    # @note：OnlyladyComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.page_size=10

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：OnlyladyComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is OnlyladyBbsComments.STEP_1:
                self.step1(params)
            elif params.step == OnlyladyBbsComments.STEP_2_BBS:
                self.step2bbs(params)
            elif params.step == OnlyladyBbsComments.STEP_3_BBS:
                self.step3bbs(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("OnlyladyComments.STEP_1")
        # 1. 根据输入原始url, 拼出评论首页
        docurl = self.r.parse('^http://bbs\.onlylady\.com\/thread-(\d+)-\d+-1\.html', params.originalurl)[0]
        # 评论首页URL
        commentinfo_url = OnlyladyBbsComments.COMMENT_URL.format(docurl=docurl, page=1)
        # 论坛
        self.storeurl(commentinfo_url, params.originalurl, OnlyladyBbsComments.STEP_2_BBS, {'docurl': docurl})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/10
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("OnlyladyComments.STEP_2")
        # 将STEP_1中的docurl传下来
        docurl = params.customized['docurl']

        xparser = XPathUtility(params.content)
        comments_count = int(xparser.getnumber('//span[@class="xi1"][2]'))
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        if cmtnum >= comments_count:
            return

        # 总数+1除以page_size，然后加1，可得到评论总页数pagecount
        page_num = int(math.ceil(float(comments_count + 1) / self.page_size))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        for page in range(1, page_num + 1, 1):
            comment_url = OnlyladyBbsComments.COMMENT_URL.format(docurl=docurl, page=page)
            self.storeurl(comment_url, params.originalurl, OnlyladyBbsComments.STEP_3_BBS, {'page': page})

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("OnlyladyComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        page = params.customized['page']
        xparser = XPathUtility(params.content)
        commentsinfo = xparser.getcomments('//div[@class="t_fsz"]/table')
        commentstimeList = []
        commentstime = self.r.parse(ur'发表于 (\d+-\d+-\d+ \d+:\d+:\d+)</em>', params.content)
        commentstime1 = self.r.parse(ur'发表于 <span title="(.+?)">', params.content)
        for commentstimeItem in commentstime:
            commentstimeList.append(commentstimeItem)
        for commentstimeItem1 in commentstime1:
            commentstimeList.append(commentstimeItem1)

        comments = []
        # 获取评论
        # 设置实际的评论量
        if page is 1:
            statrIndex = 1
        else:
            statrIndex = 0
        for index in range(statrIndex, len(commentstimeList), 1):
            content = commentsinfo[index]
            curtime = TimeUtility.getuniformtime(commentstimeList[index])
            nick = ''
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        #     cmti = CommentInfo()
        #     if URLStorage.storeupdatetime(params.originalurl, commentstimeList[index]):
        #         # 获取增加的评论（根据时间比较）
        #         cmti.content = commentsinfo[index]
        #         comments.append(cmti)
        # # 保存获取到的评论
        # if len(comments) > 0:
        #     self.commentstorage.store(params.originalurl, comments)

