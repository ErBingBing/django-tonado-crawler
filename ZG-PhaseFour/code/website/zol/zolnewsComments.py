# encoding=utf8

##############################################################################################
# @file：ZolnewsComments.py
# @author：QW_Liang
# @date：2017/9/16
# @version：Ver0.0.0.100
# @note：中关村论坛获取评论的文件
##############################################################################################
import traceback
import math
import time
from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：ZolnewsComments
# @author：QW_Liang
# @date：2017/9/16
# @note：中关村论坛获取评论的类，继承于WebSite类
##############################################################################################
class ZolnewsComments(SiteComments):
    COMMENT_URL_NEWS = 'http://comment.zol.com.cn/{kindid}/{docurl}_0_0_{page}.html?#allCommment'
    COMMENT_URL_PICTURES = 'http://comment.zol.com.cn/{kindid}/{docurl}_0_0_{page}.html#tolist'
    PAGE_SIZE=50.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：ZolnewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        self.url = ZolnewsComments.COMMENT_URL_NEWS

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is ZolnewsComments.STEP_1:
                self.step1news(params)
            elif params.step == ZolnewsComments.STEP_2:
                self.step2news(params)
            elif params.step == ZolnewsComments.STEP_3:
                self.step3news(params)
            else:
                Logger.getlogging().error('params.step == {step}'.format(step=params.step))
                return
        except Exception, e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1news(self, params):
        Logger.getlogging().info("ZolnewsComments.STEP_1")

        # ZOL游戏频道图片页
        if self.r.match('http://\w+.zol.com.cn/slide/.*', params.originalurl):
            docurl = self.r.parse('^http://\w+\.zol\.com\.cn\/slide\/\d+\/(\d+)', params.originalurl)[0]
            self.url = ZolnewsComments.COMMENT_URL_PICTURES
        # ZOL游戏频道新闻页
        elif self.r.match('http://\w+.zol.com.cn/.*', params.originalurl):
            docurl = self.r.parse('^http://\w+\.zol\.com\.cn\/\d+\/(\d+)\.html', params.originalurl)[0]
        else:
            return
        kindid = self.r.parse('kindid\s*=\s*(\w+)', params.content)[0]
        # 评论首页URL
        commentinfo_url = self.COMMENT_URL_NEWS.format(kindid=kindid, docurl=docurl, page=1)
        # 论坛
        self.storeurl(commentinfo_url, params.originalurl, ZolnewsComments.STEP_2, {'kindid':kindid, 'docurl': docurl})

    ##############################################################################################
    # @functions：step2news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2news(self, params):
        Logger.getlogging().info("ZolbbsComments.STEP_2")
        kindid = params.customized['kindid']
        docurl = params.customized['docurl']
        xparser = XPathUtility(params.content)
        comments_count = int(xparser.getlist('//*[@class="comment-num"]')[0])
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        if cmtnum >= comments_count:
            return
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        for page in range(1, page_num + 1, 1):
            comment_url = self.COMMENT_URL_NEWS.format(kindid=kindid, docurl=docurl, page=page)
            self.storeurl(comment_url, params.originalurl, ZolnewsComments.STEP_3)

    ##############################################################################################
    # @functions：step3news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3news(self, params):
        Logger.getlogging().info("ZolbbsComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        xparser = XPathUtility(params.content)
        commentsinfo = xparser.getcomments('//*[@class="comment-list-new"]//*[@class="commli"]/p')
        commentstime = xparser.getcomments('//*[@class="comment-list-new"]//*[@class="published-time"]')
        commentsnick = xparser.getcomments('//*[@class="comment-list-new"]//*[@class="user-name"]')
        # 获取评论，设置实际的评论量
        for index in range(0, len(commentstime), 1):
            # 提取时间
            tm = commentstime[index].strip()
            try:
                curtime = TimeUtility.getuniformtime(getuniformtime(tm), u'%Y-%m-%d %H:%M')
            except Exception, e:
                curtime = getuniformtime(tm)

            # 提取评论内容
            content = commentsinfo[index]
            nick = commentsnick[index]
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
