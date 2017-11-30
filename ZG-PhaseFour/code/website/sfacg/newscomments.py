# coding=utf-8

##############################################################################################
# @file：newscomments.py
# @author：Hedian
# @date：2016/12/29
# @version：Ver0.0.0.100
# @note：SF互动传媒网新闻获取评论的文件
##############################################################r################################
from log.spiderlog import Logger

from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
import math
from lxml import etree


##############################################################################################
# @class：NewsComments
# @author：Hedian
# @date：2016/12/29
# @note：SF互动传媒网新闻获取评论的类，继承于SiteComments类
##############################################################################################
class NewsComments(SiteComments):
    NEWS_COMMENTS_URL = 'http://news.sfacg.com/Comment/CommentList.aspx?Key={key}&PageIndex={pg}'
    COMIC_COMMENTS_UTL = 'http://mh.sfacg.com/Comment/CommentList.aspx?Key={key}&PageIndex={pg}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    NEWS_LIMIT = 30
    COMMIC_LIMIT = 10

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/29
    # @note：NewsComments类的构造器，初始化内部变量
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
    # @author：Hedian
    # @date：2016/12/29
    # @note：Step1：通过共通模块传入的原始url获取到Key，拼出获取评论首页的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取其他评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):

        try:
            if params.step is NewsComments.STEP_1:
                #Step1: 通过原始url得到Key，得到获取评论的首页url
                urlsplit = params.originalurl.split('/')
                field = params.customized['field']
                if field == 'news':
                    fnamesplit = urlsplit[-1].split('.')
                    key = fnamesplit[0]
                    comments_url = self.NEWS_COMMENTS_URL.format(key=key, pg=1)
                elif field == 'comic':
                    if len(urlsplit[-1].strip()) > 0:
                        key = urlsplit[-1]
                    else:
                        key = urlsplit[-2]
                    comments_url = self.COMIC_COMMENTS_UTL.format(key=key, pg=1)
                else:
                    return
                self.storeurl(comments_url, params.originalurl, self.STEP_2, {'key': key, 'field': field})

            elif params.step == NewsComments.STEP_2:

                html = etree.HTML(params.content)
                comments_total_xpath = html.xpath('//*[contains(@class,"li_more")]/strong[1]')

                if comments_total_xpath:
                    comments_total = int(comments_total_xpath[0].text)
                    cmtnum = URLStorage.getcmtnum(params.originalurl)
                    if cmtnum >= comments_total:
                        return
                    URLStorage.setcmtnum(params.originalurl, comments_total)

                    # 获取首页评论
                    self.geturlcomments(params)

                    key = params.customized['key']
                    field = params.customized['field']
                    if field == 'news' and comments_total > self.NEWS_LIMIT:
                        page_max = int(math.ceil(float(comments_total)/self.NEWS_LIMIT))

                        # 拼出首页之外的所有评论url
                        for page in range(2, page_max+1, 1):
                            comments_url = self.NEWS_COMMENTS_URL.format(key=key, pg=page)
                            self.storeurl(comments_url, params.originalurl, self.STEP_3)
                    elif field == 'comic' and comments_total > self.COMMIC_LIMIT:
                        page_max = int(math.ceil(float(comments_total) / self.COMMIC_LIMIT))

                        # 拼出首页之外的所有评论url
                        for page in range(2, page_max + 1, 1):
                            comments_url = self.COMIC_COMMENTS_UTL.format(key=key, pg=page)
                            self.storeurl(comments_url, params.originalurl, self.STEP_3)
                    else:
                        return

            elif params.step == NewsComments.STEP_3:
                # 获取评论
                self.geturlcomments(params)

            else:
                pass
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：geturlcomments
    # @params：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/12/29
    # @note：保存获取的评论。
    ##############################################################################################
    def geturlcomments(self, params):
        # 获取具体评论
        xparser = XPathUtility(params.content)
        comments_xpath = xparser.xpath('//*[contains(@id, "cm_")]')
        if not comments_xpath:
            return

        # 获取发布时间
        ip_pubtimes_xpath = xparser.getlist('//*[contains(@id,"CList___CommentList_UserLink_")]/..')

        if len(comments_xpath) == len(ip_pubtimes_xpath):
            comments = []
            # 获取评论
            for index in range(0, len(comments_xpath), 1):
                cmti = CommentInfo()
                if URLStorage.storeupdatetime(params.originalurl, getuniformtime(ip_pubtimes_xpath[index])):
                    # 获取增加的评论（根据时间比较）
                    cmti.content = comments_xpath[index].text
                    comments.append(cmti)

            # 保存获取的评论
            if len(comments) > 0:
                self.commentstorage.store(params.originalurl, comments)




