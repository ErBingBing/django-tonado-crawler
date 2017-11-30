# encoding=utf8

##############################################################################################
# @file：Ea3wcomments.py
# @author：YuXiaoye
# @date：2016/12/6
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################

import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility
from utility.gettimeutil import getuniformtime
import datetime

##############################################################################################
# @class：Ea3wcomments
# @author：YuXiaoye
# @date：2016/12/6
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################
class Ea3wcomments(SiteComments):
    COMMENT_URL = 'http://{docurl}/include/article_comments_iframe_2014.php?id={id}'
    STEP_1 = None
    STEP_2_BBS = '2'
    STEP_3_BBS = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：Ea3wcomments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：Ea3wcomments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            # 1. 根据输入原始url, 得到网站的子域名
            field = self.r.parse('^http[s]{0,1}://(\w+)\.ea3w\.com\/.*', params.originalurl)[0]
            if field == 'k':
                self.getkurlcomments(params)
            elif field == 'try':
                Logger.getlogging().debug("No comments")
                return
            else:
                if params.step is Ea3wcomments.STEP_1:
                    self.step1(params)
                elif params.step == Ea3wcomments.STEP_2_BBS:
                    self.step2bbs(params)
                elif params.step == Ea3wcomments.STEP_3_BBS:
                    self.step3bbs(params)
                else:
                    return
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("Ea3wcomments.STEP_1")
        docurl = self.r.parse('^http://(.*)/\d+\/\d+.html', params.originalurl)[0]
        id = self.r.parse('^http://\w+.ea3w.com/\d+\/(\d+).html', params.originalurl)[0]
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = Ea3wcomments.COMMENT_URL.format(id=id,docurl=docurl)
        self.storeurl(commentinfo_url, params.originalurl, Ea3wcomments.STEP_2_BBS,{'commentinfo_url':commentinfo_url})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("Ea3wcomments.STEP_2")
        commentinfo_url = params.customized['commentinfo_url']+"&load=all"
        xparser = XPathUtility(params.content)
        comments_count = xparser.getnumber('//div[@class="at-comment"]/a/span')
        # 保存页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)
        self.storeurl(commentinfo_url, params.originalurl, Ea3wcomments.STEP_3_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/6
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("Ea3wcomments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        xparser = XPathUtility(params.content)
        commentsinfo = xparser.getcomments('//p[@class="comment-content"]')
        commentstime = xparser.getcomments('//span[@class="time"]')
        comments = []

        # 获取评论
        for index in range(0, int(len(commentsinfo)), 1):
            # 提取时间
            cmti = CommentInfo()
            cmti.content = commentsinfo[index]

            if str(commentstime[index]).strip().decode("utf8") == '刚刚'.decode("utf8"):
                tm = getuniformtime(str(datetime.datetime.now()))
            else:
                tm = getuniformtime(str(commentstime[index]))
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)
        # 保存获取到的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)

    ##############################################################################################
    # @functions：getkurlcomments
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/12/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def getkurlcomments(self, params):
        xparser = XPathUtility(params.content)
        # 获取评论列表
        comments_xpath = xparser.xpath('//*[@class="page-pl-list-text"]')
        # 获取评论时间
        pubtime_xpath = xparser.xpath('//*[@class="page-pl-user-timer"]')

        if len(comments_xpath) >= len(pubtime_xpath):
            start = len(comments_xpath) - len(pubtime_xpath)
            comments = []
            for index in range(start, len(comments_xpath), 1):
                if URLStorage.storeupdatetime(params.originalurl, getuniformtime(pubtime_xpath[index].text)):
                    cmti = CommentInfo()
                    cmti.content = comments_xpath[index].text
                    comments.append(cmti)

            # 保存获取到的评论
            if len(comments) > 0:
                self.commentstorage.store(params.originalurl, comments)
