# coding=utf-8

##############################################################################################
# @file：zonghengBookComments.py
# @author：QW_Liang
# @date：2017/9/16
# @version：Ver0.0.0.100
# @note：纵横书库获取评论的文件
###############################################################################################
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime
from utility.timeutility import TimeUtility
import math
import time
##############################################################################################
# @class：BookComments
# @author：QW_Liang
# @date：2017/9/16
# @note：纵横书库获取评论的类，继承于SiteComments类
##############################################################################################
class BookComments(SiteComments):
    # 分支条件
    STEP_2 = '2_book'
    STEP_3 = '3_book'
    page_size = 30.0
    # COMMENTS_URL = 'http://book.zongheng.com/ajax/book.comment.getThreadL1st2.do?bookId={bookId}&pageNum={pageno}'
    COMMENTS_URL = 'http://book.zongheng.com/api/book/comment/getThreadL1st2.htm'
    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：BookComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：getcomments_step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def getcomments_step1(self, params):
        bookId = int(self.r.parse('^http://book\.zongheng\.com/book/(\d+).html$', params.url)[0])
        Logger.getlogging().debug(bookId)
        commentinfo_url = BookComments.COMMENTS_URL
        self.storeposturl(commentinfo_url, params.originalurl, BookComments.STEP_2,{'bookId': bookId,'pageNum':'1'},{'bookId': bookId})

    ##############################################################################################
    # @functions：getcomments_step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def getcomments_step2(self, params):

        bookId = params.customized['bookId']
        xhtml = XPathUtility(html=params.content)
        comments_count = int(xhtml.getstring('//*[@class="fr"]/em'))
        Logger.getlogging().debug(comments_count)

        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        page_num = int(math.ceil(float(comments_count - cmtnum) / self.page_size))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        for page in range(1, page_num + 1, 1):
            comment_url = BookComments.COMMENTS_URL
            self.storeposturl(comment_url, params.originalurl, BookComments.STEP_3,{'bookId': bookId,'pageNum':page})

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

        contents = xhtml.getlist('//*[contains(@id,"partThreadContent")]')
        curtimes = xhtml.getlist('//*[@class="comment_rw"]/span/em')
        nicks = xhtml.getlist('//*[@class="wzbox"]/h5')
        for index in range(0, len(contents), 1):
            curtime = TimeUtility.getuniformtime(curtimes[index]+':00')
            content = str(contents[index])
            nick = str(nicks[index])
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
