# encoding=utf8

##############################################################################################
# @file：Flash8Comments.py
# @author：HuBorui
# @date：2016/12/01
# @version：Ver0.0.0.100
# @note：闪8获取评论的文件
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
from  bs4 import  BeautifulSoup

##############################################################################################
# @class：Flash8Comments
# @author：HuBorui
# @date：2016/12/01
# @note：闪8获取评论的类，继承于WebSite类
##############################################################################################
class Flash8Comments(SiteComments):
    COMMENT_URL = 'http://www.flash8.net/newgbook/list_iframe.aspx?nsort=flash&iid={docurl}&page={page}'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/12/01
    # @note：Flash8Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/12/01
    # @note：Flash8Comments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Flash8Comments.STEP_1:
                self.step1(params)
            elif params.step == Flash8Comments.STEP_2:
                self.step2(params)
            elif params.step == Flash8Comments.STEP_3:
                self.step3(params)
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
    # @date：2016/12/01
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("Flash8Comments.STEP_1")

        # 1. 根据输入原始url, 拼出评论首页
        docurl = self.r.parse('^http://www\.flash8\.net\/flash\/(\d+)\.shtml', params.originalurl)[0]
        # 评论首页URL
        commentinfo_url = 'http://www.flash8.net/newgbook/list_iframe.aspx?nsort=flash&iid={docurl}&page=1'.format(docurl=docurl)
        # 论坛
        self.storeurl(commentinfo_url, params.originalurl, Flash8Comments.STEP_2, {'docurl': docurl})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/12/01
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("Flash8Comments.STEP_2")
        # 将STEP_1中的docurl传下来
        docurl = params.customized['docurl']
        xparser = XPathUtility(params.content)
        commentsinfo = xparser.getstring('//div[@class="page"]/span/font[1]')

        # 保存页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= int(commentsinfo[0]):
            return
        URLStorage.setcmtnum(params.originalurl, int(commentsinfo[0]))

        # 总数除以page_size，然后加1，可得到评论总页数comments_count
        pagecount = xparser.getnumber('//*[@class="pg"]/label/span')
        if pagecount == 0:
            pagecount = pagecount + 1

        for page in range(1, pagecount + 1, 1):
            comment_url = Flash8Comments.COMMENT_URL.format(docurl=docurl, page=page)
            self.storeurl(comment_url, params.originalurl, Flash8Comments.STEP_3, {'page': page})

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/12/01
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("Flash8Comments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        page = params.customized['page']
        xparser = XPathUtility(params.content)
        commentsinfo = xparser.getcomments('//td[@class="t_f"]')
        #commentstime = self.r.parse(ur'发表于 (\d+-\d+-\d+ \d+:\d+)</em>', params.content)
        commentstime = xparser.getcomments('//div[@class="authi"]/em')

        comments = []

        # 获取评论
        # 设置实际的评论量
        if page is 1:
            statrIndex = 1
        else:
            statrIndex = 0
        for index in range(statrIndex, len(commentstime), 1):
            cmti = CommentInfo()
            if URLStorage.storeupdatetime(params.originalurl, commentstime[index]):
                # 获取增加的评论（根据时间比较）
                cmti.content = commentsinfo[index]
                comments.append(cmti)
        # 保存获取到的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)
