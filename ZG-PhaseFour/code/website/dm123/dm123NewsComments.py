# encoding=utf8

##############################################################################################
# @file：dm123comments.py
# @author：HuBorui
# @date：2016/12/6
# @version：Ver0.0.0.100
# @note：动漫FANS获取评论的文件
##############################################################################################

import math
import traceback
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments

##############################################################################################
# @class：dm123Comments
# @author：HuBorui
# @date：2016/12/6
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class Dm123NewsComments(SiteComments):
    COMMENT_URL ='http://www.dm123.cn/e/po/index.php?page={page}&classid={classid}&id={id}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/12/6
    # @note：构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.page_size=10

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    # @author：HuBorui
    # @date：2016/12/6
    # @note：Step1：通过共通模块传入的html内容获取到key,生成当前页数和总页数，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Dm123NewsComments.STEP_1:
                self.step1(params)
            elif params.step == Dm123NewsComments.STEP_2:
                self.step2(params)
            elif params.step == Dm123NewsComments.STEP_3:
                self.step3(params)
            else:
                Logger.getlogging().error('params.step == {step}'.format(step=params.step))
                return
        except Exception, e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/9
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("DmOneTwoThreeNewsComments.STEP_1")
        id = self.r.parse('^http://www.dm123.cn/.*/(\d+).html', params.originalurl)[0]
        xparser = XPathUtility(params.content)
        classid = xparser.xpath("//input[@id='classid']/@value")[0]

        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = Dm123NewsComments.COMMENT_URL.format(page=0, classid=classid, id=id)
        # 评论首页URL
        # 论坛
        self.storeurl(commentinfo_url, params.originalurl, Dm123NewsComments.STEP_2, {'classid': classid, 'id': id})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/9
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("Dm123NewsComments.STEP_2")
        classid = params.customized['classid']
        id = params.customized['id']
        xparser = XPathUtility(params.content)
        # 评论总数(当评论不满一页时，直接获取到的comments_count为0)
        comments_count = xparser.getnumber('//div/a[1]/b')

        # comments_count为0时分两种情况，真的没有评论和有评论
        if 0 == comments_count:
            commentsinfos = xparser.getcomments('//div[@class="rbvalueout"]')
            commentstimes = xparser.getcomments('//span[@class="rbtime"]')
            # comments_count重新赋值
            comments_count = len(commentsinfos)
            if 0 == comments_count:
                return
            else:
                # 判断增量
                cmtnum = URLStorage.getcmtnum(params.originalurl)
                if cmtnum >= comments_count:
                    return
                URLStorage.setcmtnum(params.originalurl, comments_count)
                self.storeurl(params.originalurl, params.originalurl, Dm123NewsComments.STEP_3,
                              {'is_only_one_page': True, 'commentsinfos': commentsinfos,
                               'commentstimes': commentstimes})
        else:
            # 判断增量
            cmtnum = URLStorage.getcmtnum(params.originalurl)
            if cmtnum >= comments_count:
                return
            URLStorage.setcmtnum(params.originalurl, comments_count)
            # 评论页数
            page_count = int(math.ceil(float(comments_count) / self.page_size))
            for page in range(0, int(page_count), 1):
                comment_url = Dm123NewsComments.COMMENT_URL.format(page=page, classid=classid, id=id)
                self.storeurl(comment_url, params.originalurl, Dm123NewsComments.STEP_3,
                              {'is_only_one_page': False})

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/9
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("Dm123NewsComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        is_only_one_page = params.customized['is_only_one_page']
        if is_only_one_page:
            commentsinfos = params.customized['commentsinfos']
            commentstimes = params.customized['commentstimes']
        else:
            xparser = XPathUtility(params.content)
            commentsinfos = xparser.getcomments('//div[@class="rbvalueout"]')
            commentstimes = xparser.getcomments('//span[@class="rbtime"]')

        comments = []
        for index in range(0, len(commentstimes)):
            commentstime = commentstimes[index].strip()
            if URLStorage.storeupdatetime(params.originalurl, commentstime):
                cmti = CommentInfo()
                cmti.content = commentsinfos[index].strip()
                comments.append(cmti)

        # 保存获取的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)
