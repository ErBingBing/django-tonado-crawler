# coding=utf-8

##############################################################################################
# @file：uuu9comments.py
# @author：Hedian
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：游久网站获取评论的文件
##############################################################r################################

from website.common.comments import SiteComments
# from utility.bbscommon import BBSCommon
from log.spiderlog import Logger

##############################################################################################
# @class：BbsComments
# @author：Hedian
# @date：2016/11/30
# @note：游久网站获取评论的类，继承于SiteComments类
##############################################################################################
class BbsComments(SiteComments):
    BBS_URL_REG = '^http://moba\.uuu9\.com/\w+-\d+-(\d+)-\d+.html'
    PAGE_SIZE = 10
    BBS_TITLE = ''
    STEP_1 = None
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/30
    # @note：Uuu9Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/30
    # @note：AppgameComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        if params.step is BbsComments.STEP_1:
            self.step1(params)
        elif params.step == BbsComments.STEP_2_BBS:
            self.step2bbs(params)
        elif params.step == BbsComments.STEP_3_BBS:
            self.step3bbs(params)
        else:
            return

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/30
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("Uuu9Comments.STEP_1")
        # 拼接获取uniqid的url
        self.storeurl(params.originalurl, params.originalurl, BbsComments.STEP_2_BBS)

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/30
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("Uuu9Comments.STEP_2_BBS")
        # 通过xpath, 从页面上获取页面总数
        lastpg = BBSCommon.gettotalpages(params.content)
        if lastpg is None:
            return

        # 当前评论页码
        pg = self.r.parse(self.BBS_URL_REG, params.url)[0]

        # 获取当前页评论
        params.customized['lastpg'] = lastpg
        BBSCommon.getpagecomments(self, params, self.BBS_URL_REG, self.PAGE_SIZE)

        # 如果只有1页，后续处理不要
        if int(lastpg) == 1:
            return

        # 对于S1, 需要展开获取所有评论
        urlArr = params.originalurl.split('-')
        if len(urlArr) != 4:
            return
        for page in range(1, lastpg + 1, 1):
            if page == int(pg):
                continue
            commentUrl = urlArr[0] + '-' + urlArr[1] + '-' + str(page) + '-' + urlArr[3]
            Logger.getlogging().debug(commentUrl)
            self.storeurl(commentUrl, params.originalurl, BbsComments.STEP_3_BBS, {'lastpg': lastpg})

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("Uuu9Comments.STEP_3_BBS")
        BBSCommon.getpagecomments(self, params, self.BBS_URL_REG, self.PAGE_SIZE)