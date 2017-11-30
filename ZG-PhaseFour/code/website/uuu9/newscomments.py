# coding=utf-8

##############################################################################################
# @file：newscomments.py
# @author：QW_Liang
# @date：2017/09/13
# @version：Ver0.0.0.100
# @note：游久新闻获取评论的文件
##############################################################r################################

import math
import time
from lxml import etree

from utility.gettimeutil import getuniformtime
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.common import Common

##############################################################################################
# @class：NewsComments
# @author：QW_Liang
# @date：2017/09/13
# @note：游久新闻获取评论的类，继承于SiteComments类
##############################################################################################
class NewsComments(SiteComments):
    COMMENT_URL = 'http://newcomment.uuu9.com/Action/commionAction.ashx?pindex={pg}&aid={aid}&site={site}&channelid={channelid}&url={oriurl}&title={title}'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2_NEWS = '2_news'
    STEP_3_NEWS = '3_news'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：NewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.r = RegexUtility()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：NewsComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        if params.step is NewsComments.STEP_1:
            self.step1(params)
        elif params.step == NewsComments.STEP_2_NEWS:
            self.step2(params)
        elif params.step == NewsComments.STEP_3_NEWS:
            self.step3(params)
        else:
            return

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        #1. 根据输入原始url, 得到site, channelid, title, aid
        site = self.r.getid('site', params.content)
        if not site:
            site = 'www'
        channelid = self.r.getid('channelid', params.content)
        if not channelid:
            return
        aid = self.r.getid('aid', params.content)
        if not aid:
            return
        title_reg = self.r.parse(u'\s*title\s*:\s*"(.*)"', params.content)
        if not title_reg:
            return
        title = Common.urlenc(title_reg[0])

        # 拼接获取评论的url
        comement_url = self.COMMENT_URL.format(pg=1, aid=aid, site=site, channelid=channelid, oriurl=params.originalurl, title=title)
        self.storeurl(comement_url, params.originalurl, NewsComments.STEP_2_NEWS,{'site':site, 'channelid':channelid, 'aid':aid, 'title':title})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：根据输入html，通过xpath得到评论总数，评论量和评论时间，拼出第一页之外的评论的url
    ##############################################################################################
    def step2(self, params):

        # html = etree.HTML(params.content)

        # 通过xpath得到评论总数
        # comment_count_xpath = html.xpath('//*[@id="comment_count"]')
        xhtml = XPathUtility(html=params.content)
        comment_count_xpath = xhtml.getstring('//*[@id="comment_count"]')
        if not comment_count_xpath:
            return
        comment_count = int(comment_count_xpath)

        # 检查页面评论量
        cmtnum = CMTStorage.getcount(params.originalurl)
        if cmtnum >= comment_count:
            return
        NewsStorage.setcmtnum(params.originalurl, comment_count)

        # 获取第一页评论
        self.geturlcomments(params)

        # 计算出最后一页评论的页数


        aid = params.customized['aid']
        site = params.customized['site']
        channelid = params.customized['channelid']
        title = params.customized['title']

        # 计算所需取的评论页数，最大10页
        lastpg = int(math.ceil(float(comment_count - cmtnum) / self.PAGE_SIZE))
        if lastpg >= self.maxpages:
            lastpg = self.maxpages

        # 拼出第一页之外的评论的url
        for page in range(2, lastpg + 1, 1):
            comement_url = self.COMMENT_URL.format(pg=page, aid=aid, site=site, channelid=channelid,
                                                   oriurl=params.originalurl, title=title)
            self.storeurl(comement_url, params.originalurl, NewsComments.STEP_3_NEWS)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：根据输入的html，得到评论
    ##############################################################################################
    def step3(self, params):
        # 获取当前页评论
        self.geturlcomments(params)


    ##############################################################################################
    # @functions：geturlcomments
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/13
    # @note：根据输入的html，获取页面评论
    ##############################################################################################
    def geturlcomments(self, params):
        # 获取页面评论
        html = etree.HTML(params.content)

        # 通过xpath得到评论时间
        postTime_xpath = html.xpath('//*[@id="NewComment"]/div/div/*[@class="postTime"]')
        if not postTime_xpath:
            return

        # 通过xpath得到评论
        comments_xpath = html.xpath('//*[@id="NewComment"]/div/div/*[@class="body"]/div')
        if not comments_xpath:
            return
        nicks_xpath = html.xpath('//*[@id="NewComment"]/div/div/*[@class="author"]/*[@class="from"]')

        if len(comments_xpath) == len(postTime_xpath):

            for index in range(0, len(comments_xpath), 1):
                curtime = getuniformtime(postTime_xpath[index].text)

                content = comments_xpath[index].text
                nick = nicks_xpath[index].text
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
