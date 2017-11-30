# encoding=utf8

##############################################################################################
# @file：SougouNewsComments.py
# @author：Ninghz
# @date：2016/12/20
# @version：Ver0.0.0.100
# @note：搜狗影视获取评论的文件
##############################################################################################

import math
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup

##############################################################################################
# @class：SougouNewsComments
# @author：Ninghz
# @date：2016/12/20
# @version：Ver0.0.0.100
# @note：搜狗影视获取评论的文件
##############################################################################################
class SougouNewsComments(SiteComments):
    COMMENT_URL = '{url}?sort=time&start={offset}'
    COMMENT_URL_PAGE = '{url}?start={href}#comments'
    Offset = 20
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'
    STEP_4 = '4'
    STEP_5 = '5'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/12/20
    # @note：SougouNewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：SougouNewsComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is SougouNewsComments.STEP_1:
                self.step1(params)
            elif params.step == SougouNewsComments.STEP_2:
                self.step2(params)
            elif params.step == SougouNewsComments.STEP_3:
                self.step3(params)
            elif params.step == SougouNewsComments.STEP_4:
                self.step4(params)
            elif params.step == SougouNewsComments.STEP_5:
                self.step5(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception:
            Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("SougouNewsComments.STEP_1")
        # 1. 获取评论跳转的url
        xhtml = XPathUtility(html=params.content)
        commentUrl = str(xhtml.xpath('//*[@class="dbcomment"]/div/a/@href')[0])
        comment_url = SougouNewsComments.COMMENT_URL.format(url=commentUrl, offset=0)
        self.storeurl(comment_url, params.originalurl, SougouNewsComments.STEP_2, {'commenturl':commentUrl})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：根据评论url获取评论总数，拼出所有评论url
    ##############################################################################################
    def step2(self,params):
        Logger.getlogging().info("SougouNewsComments.STEP_2")
        commenturl = params.customized['commenturl']
        xhtml = XPathUtility(html=params.content)
        comments_count = xhtml.getnumber('//span[@class="count"]')
        # 保存页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)
        for index in range(0, int(math.ceil(comments_count/SougouNewsComments.Offset)), 1):
            commentinfo_url = SougouNewsComments.COMMENT_URL.format(url=commenturl, offset=index * SougouNewsComments.Offset)
            self.storeurl(commentinfo_url, params.originalurl, SougouNewsComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：根据输入的html(json文件），得到评论内容链接
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("SougouNewsComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        xhtml = XPathUtility(params.content)
        #查询详细评论的链接集合
        commentshref = xhtml.xpath('//*[@class="title"]/a/@href')
        for href in commentshref:
            self.storeurl(href, params.originalurl, SougouNewsComments.STEP_4)

    ##############################################################################################
    # @functions：step4
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step4(self, params):
        Logger.getlogging().info("SougouNewsComments.STEP_4")
        try:
            soup = BeautifulSoup(params.content, 'html5lib')
            info = soup.select('.review-content')[0]
            updatetime = soup.select('.main-meta')[0].get_text()
        except:
            Logger.getlogging().error('{0}:30000 No comments'.format(params.originalurl))
            #Logger.printexception()
            return
            
        comments = []
        # 提取时间
        
        if URLStorage.storeupdatetime(params.originalurl, updatetime):
            cmti = CommentInfo()
            cmti.content = info.get_text()
            comments.append(cmti)

        # 取得影评中评论
        hrefs = self.r.parse(ur'start=(\d+)', params.content)
        if len(hrefs) == 0:
            commentsInfo = soup.select('.comment-text')
            commentsInfoTime = soup.select('.report-comment')
            for index in range(0, len(commentsInfo), 1):
                publicTime = self.r.parse(ur'(\d+-\d+-\d+ \d+:\d+:\d+)', commentsInfoTime[index].get_text())[0]
                if URLStorage.storeupdatetime(params.originalurl, publicTime):
                    cmti = CommentInfo()
                    cmti.content = commentsInfo[index].get_text()
                    comments.append(cmti)
        else:
            self.storeurl(params.url, params.originalurl, SougouNewsComments.STEP_5)
            for index in range(0, len(hrefs) -2, 1):
                commentinfo_url = SougouNewsComments.COMMENT_URL_PAGE.format(url=params.url, href=hrefs[index])
                self.storeurl(commentinfo_url, params.originalurl, SougouNewsComments.STEP_5)

        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)

    ##############################################################################################
    # @functions：step5
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/20
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step5(self, params):
        soup = BeautifulSoup(params.content, 'html5lib')
        commentsInfo = soup.select('.comment-text')
        commentsInfoTime = soup.select('.report-comment')
        comments = []
        for index in range(0, len(commentsInfo), 1):
            publicTime = self.r.parse(ur'(\d+-\d+-\d+ \d+:\d+:\d+)', commentsInfoTime[index].get_text())[0]
            if URLStorage.storeupdatetime(params.originalurl, publicTime):
                cmti = CommentInfo()
                cmti.content = commentsInfo[index].get_text()
                comments.append(cmti)

        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)