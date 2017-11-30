# coding=utf-8

##############################################################################################
# @file：bookcomments.py
# @author：Hedian
# @date：2016/12/29
# @version：Ver0.0.0.100
# @note：SF互动传媒网漫画获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/12
# @note:第80-87行添加了对manhua子网站pubtime时间的过滤与抽取
##############################################################r################################
from log.spiderlog import Logger

from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from storage.basicinfostorage import BaseInfoStorage
from utility.xpathutil import XPathUtility
import math
from lxml import etree
import re


##############################################################################################
# @class：BookComments
# @author：Hedian
# @date：2016/12/29
# @note：SF互动传媒网新闻获取评论的类，继承于SiteComments类
##############################################################################################
class BookComments(SiteComments):
    MANHUA_COMMENTS_URL = 'http://manhua.sfacg.com/mh/{key}/scmts/{pg}/'
    BOOK_COMMENTS_URL = 'http://book.sfacg.com/cmts/{key}/{pg}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    limit = 10

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/29
    # @note：BookComments类的构造器，初始化内部变量
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
            if params.step is BookComments.STEP_1:
                #Step1: 通过原始url得到Key，得到获取评论的首页url
                urlsplit = params.originalurl.split('/')
                if len(urlsplit[-1].strip()) > 0:
                    key = urlsplit[-1]
                else:
                    key = urlsplit[-2]

                field = params.customized['field']
                if field == 'manhua':
                    comments_url = self.MANHUA_COMMENTS_URL.format(key=key, pg=1)
                    
                    hxpath = XPathUtility(params.content)
                    pubTime = hxpath.getstring('//*[@class="synopsises_font"]/li[2]/text()',' ')
                    if pubTime:
                        pubTime = pubTime[0]
                        pubTime = re.findall('\d+/\d+/\d+',params.content)[0]
                        info = BaseInfoStorage.getbasicinfo(params.originalurl)
                        info.pubtime = pubTime
                        BaseInfoStorage.store(params.originalurl, info)            
                    
                elif field == 'book':
                    comments_url = self.BOOK_COMMENTS_URL.format(key=key, pg=1)
                else:
                    return
                self.storeurl(comments_url, params.originalurl, self.STEP_2, {'key': key, 'field': field})

            elif params.step == BookComments.STEP_2:

                html = etree.HTML(params.content)
                comments_total_xpath = html.xpath('//*[@class="content_title"]/span/a')

                if comments_total_xpath:
                    comments_total_str = self.r.parse(u'(\d+)', comments_total_xpath[0].text.replace(',', ''))
                    if not comments_total_str:
                        return

                    comments_total = int(comments_total_str[0])
                    cmtnum = URLStorage.getcmtnum(params.originalurl)
                    if cmtnum >= comments_total:
                        return
                    URLStorage.setcmtnum(params.originalurl, comments_total)

                    # 获取首页评论
                    self.geturlcomments(params)

                    if comments_total > self.limit:
                        page_max = int(math.ceil(float(comments_total)/self.limit))

                        # 拼出首页之外的所有评论url
                        key = params.customized['key']
                        field = params.customized['field']
                        if field == 'manhua':
                            for page in range(2, page_max+1, 1):
                                comments_url = self.MANHUA_COMMENTS_URL.format(key=key, pg=page)
                                self.storeurl(comments_url, params.originalurl, self.STEP_3)
                        elif field == 'book':
                            for page in range(2, page_max+1, 1):
                                comments_url = self.BOOK_COMMENTS_URL.format(key=key, pg=page)
                                self.storeurl(comments_url, params.originalurl, self.STEP_3)
                        else:
                            return

            elif params.step == BookComments.STEP_3:
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
        comments_xpath = xparser.xpath('//*[@id="short_comment_content"]')
        if not comments_xpath:
            return

        # 获取发布时间
        ip_pubtimes_xpath = xparser.getlist('//*[@id="short_comment_left"]')

        if len(comments_xpath) == len(ip_pubtimes_xpath):
            comments = []
            # 获取评论
            for index in range(0, len(comments_xpath), 1):
                cmti = CommentInfo()
                publicTime = ip_pubtimes_xpath[index]
                if self.r.search(ur'\d{2}-\d+-\d+ \d+:\d+', publicTime):
                    publicTime = '20' + self.r.parse(ur'\d{2}-\d+-\d+ \d+:\d+', publicTime)[0]

                if self.r.search(ur'\d+/\d+/\d+ \d+:\d+:\d+', publicTime):
                    publicTime = self.r.parse(ur'\d+/\d+/\d+ \d+:\d+:\d+', publicTime)[0]

                if URLStorage.storeupdatetime(params.originalurl, getuniformtime(publicTime)):
                    # 获取增加的评论（根据时间比较）
                    cmti.content = comments_xpath[index].text
                    comments.append(cmti)

            # 保存获取的评论
            if len(comments) > 0:
                self.commentstorage.store(params.originalurl, comments)




