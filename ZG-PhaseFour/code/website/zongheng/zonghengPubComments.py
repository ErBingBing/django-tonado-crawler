# coding=utf-8

##############################################################################################
# @file：zonghengBookComments.py
# @author：QW_Liang
# @date：2017/9/16
# @version：Ver0.0.0.100
# @note：纵横图书获取评论的文件
###############################################################################################
import time
import math
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime
from utility.timeutility import TimeUtility

##############################################################################################
# @class：PubComments
# @author：QW_Liang
# @date：2017/9/16
# @note：纵横图书获取评论的类，继承于SiteComments类
##############################################################################################
class PubComments(SiteComments):
    # 分支条件
    STEP_2 = '2_pub'
    STEP_3 = '3_pub'
    PAGE_SIZE = 30.0
    # COMMENTS_URL = 'http://pub.zongheng.com/ajax/book.comment.getThreadL1st.do?bookId={bookId}&pageNum={pageno}'
    COMMENTS_URL = 'http://pub.zongheng.com/ajax/book.comment.getThreadL1st.do'
    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Ninghz
    # @date：2016/12/06
    # @note：PubComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：getcomments_step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/06
    # @note：根据输入url，拼出获取评论页数的url
    ##############################################################################################
    def getcomments_step1(self, params):
        bookId = int(self.r.parse('^http://pub\.zongheng\.com/book/(\d+).html$', params.url)[0])
        Logger.getlogging().debug(bookId)
        # commentinfo_url = PubComments.COMMENTS_URL.format(bookId=bookId, pageno=1)
        commentinfo_url = PubComments.COMMENTS_URL
        self.storeposturl(commentinfo_url, params.originalurl, PubComments.STEP_2,{'bookId': bookId,'pageNum':'1'},{'bookId': bookId})

    ##############################################################################################
    # @functions：getcomments_step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/6
    # @note：根据输入html，拼出获取所有评论的url
    ##############################################################################################
    def getcomments_step2(self, params):
        bookId = params.customized['bookId']
        xhtml = XPathUtility(html=params.content)
        page_counts = int(xhtml.xpath('//div[@class="page"]/@pagenum')[0])
        comments_count = int(xhtml.xpath('//div[@class="page"]/@total')[0])
        Logger.getlogging().debug(comments_count)
        if page_counts == 0:
            return
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return

        page_num = int(math.ceil(float(comments_count - cmtnum)/self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        for page in range(1, page_num+1, 1):
            comment_url = PubComments.COMMENTS_URL
            self.storeposturl(comment_url, params.originalurl, PubComments.STEP_3,{'bookId': bookId,'pageNum':page})

    ##############################################################################################
    # @functions：getcomments_step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入html，得到评论
    ##############################################################################################
    def getcomments_step3(self, params):
        xhtml = XPathUtility(html=params.content)
        contents = xhtml.getlist('//*[@class="wz"]/p')
        curtimes = xhtml.getlist('//*[@class="fr"]')
        nicks = xhtml.getlist('//*[@class="wzbox"]/h5')

        for index in range(0, len(contents), 1):
            curtime = curtimes[index][4:]+':00'
            Logger.getlogging().debug(contents[index])
            content = str(contents[index])
            nick = str(nicks[index])
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)