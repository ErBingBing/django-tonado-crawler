# encoding=utf-8
##############################################################################################
# @file：ptbusNewsComments.py
# @author：Yangming
# @date：2016/12/15
# @version：Ver0.0.0.100
# @note：口袋巴士获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql

###############################################################################################
import time
from storage.newsstorage import NewsStorage
from website.common.comments import SiteComments
from log.spiderlog import Logger
import traceback
from utility.xpathutil import XPathUtility
from storage.cmtstorage import CMTStorage
from utility.md5 import MD5
from utility.gettimeutil import TimeUtility


##############################################################################################
# @class：PtbusNewsComments
# @author：Yangming
# @date：2016/12/15
# @note：口袋巴士获取评论的类，继承于SiteComments类
##############################################################################################
class PtbusNewsComments(SiteComments):
    COMMENTS_URL = 'http://cmt.ptbus.com/comment/?url={url}&token={token}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yangming
    # @date：2016/12/15
    # @note：口袋巴士类的构造器，初始化内部变量

    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Yangming
    # @date：2016/12/15
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is PtbusNewsComments.STEP_1:
                self.step1(params)
            elif params.step == PtbusNewsComments.STEP_2:
                self.step2(params)
            elif params.step == PtbusNewsComments.STEP_3:
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
    # @date：2016/12/15
    # @note：根据主页获取评论ID及评论地址
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("PtbusNewsComments.STEP_1")

        standard_url = params.originalurl
        if '/' != standard_url[-1]:
            standard_url += '/'
        comments_url = PtbusNewsComments.COMMENTS_URL.format(url=standard_url, token=MD5().m(standard_url))
        self.storeurl(comments_url, params.originalurl, PtbusNewsComments.STEP_2, {'comments_url': comments_url})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/9
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("PtbusNewsComments.STEP_2")
        comments_url = params.customized['comments_url']

        xparser = XPathUtility(params.content)
        comments_count = xparser.getcomments("//span[@class='totleNum']")[0][0]
        if comments_count:
            NewsStorage.setcmtnum(params.originalurl, comments_count)
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return


        # 取得评论个数
        self.storeurl(comments_url, params.originalurl, PtbusNewsComments.STEP_3, {'comments_url': comments_url})

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/2
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("PtbusNewsComments.STEP_3")
        xparser = XPathUtility(params.content)
        comments = []
        comments_infos = xparser.getcomments("//div[@class='comment-item cl']/text()[2]")
        comments_times = xparser.getcomments("//span[@class='fl postTime']")
        comments_nicks = xparser.getcomments("//span[@class='text-tit fl f12']")
        for index in range(0, len(comments_infos)):
            # curtime = TimeUtility.getuniformtime(comments_times[index], u'发表于：%Y-%m-%d %H:%M')
            curtime = TimeUtility.getuniformtime(comments_times[index], u'%Y-%m-%d %H:%M')
            comment_text = comments_infos[index][1:len(comments_infos[index])]
            content = comment_text
            nick = comments_nicks[index][0:len(comments_nicks[index])]
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
            # if URLStorage.storeupdatetime(params.originalurl, tm):
            #     cmti = CommentInfo()
            #     comment_text = comments_infos[index][1:len(comments_infos[index])]
            #     cmti.content = comment_text
            #     comments.append(cmti)

        # # 保存获取的评论
        # if len(comments) > 0:
        #     self.commentstorage.store(params.originalurl, comments)
