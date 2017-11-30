# encoding=utf-8
##############################################################################################
# @file：xinhuaNewsComments.py
# @author：QW_Liang
# @date：2017/09/16
# @version：Ver0.0.0.100
# @note：新华网获取评论的文件
###############################################################################################
import traceback
import json
import time
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：xinhuaNewsComments
# @author：QW_Liang
# @date：2017/09/16
# @note：新华网获取评论的类，继承于SiteComments类
##############################################################################################
class xinhuaNewsComments(SiteComments):
    COMMENTS_URL_NEWS = 'http://comment.home.news.cn/a/newsCommAll.do?_ksTS=1478591354350_166&newsId=1-{newsId}&pid={pid}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：新华网类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.pid = 1

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：xinhuaComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is xinhuaNewsComments.STEP_1:
                self.step1(params)
            elif params.step == xinhuaNewsComments.STEP_2:
                self.step2(params)
            elif params.step == xinhuaNewsComments.STEP_3:
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
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：根据主页获取评论ID及评论地址
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("xinhuaComments.STEP_1")
        newsId = self.r.parse('^http://.*_(\d+)\.htm', params.originalurl)[0]
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = xinhuaNewsComments.COMMENTS_URL_NEWS.format(newsId=newsId, pid=self.pid)
        self.storeurl(commentinfo_url, params.originalurl, xinhuaNewsComments.STEP_2, {'newsId': newsId})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        try:
            Logger.getlogging().info("xinhuaComments.STEP_2")
            # 将STEP_1中的commentinfo_url传下来
            newsId = params.customized['newsId']
            comments_info = json.loads(params.content)
            comments_count = comments_info['totalRows']
            NewsStorage.setcmtnum(params.originalurl, comments_count)
            page_count = comments_info['totalPage']

            # 判断增量
            cmtnum = CMTStorage.getcount(params.originalurl,True)
            if cmtnum >= comments_count:
                return

            # 判断增量
            if page_count >= self.maxpages:
                page_count = self.maxpages

            for index in range(0, int(page_count)):
                commentinfo_url = xinhuaNewsComments.COMMENTS_URL_NEWS.format(newsId=newsId, pid=(index + 1))
                self.storeurl(commentinfo_url, params.originalurl, xinhuaNewsComments.STEP_3)
        except:
            Logger.printexception()
    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/16
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("xinhuaComments.STEP_3")
        # Step3: 通过Step1设置的urls，得到所有评论，抽取评论
        comment_json = json.loads(params.content)

        for key in range(0, len(comment_json['contentAll'])):
            curtime = TimeUtility.getuniformtime(comment_json['contentAll'][key]['commentTime'])
            content = comment_json['contentAll'][key]['content']
            nick = comment_json['contentAll'][key]['nickName']
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
