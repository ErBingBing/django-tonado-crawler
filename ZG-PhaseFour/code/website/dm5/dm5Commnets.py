# encoding=utf8

##############################################################################################
# @file：Dm5Commnets.py
# @author：HuBorui
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：动漫屋新闻获取评论的文件
##############################################################################################

import traceback
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from bs4 import BeautifulSoup
from utility.gettimeutil import getuniformtime 

##############################################################################################
# @class：Dm5Commnets
# @author：HuBorui
# @date：2016/11/30
# @note：动漫屋新闻获取评论的类，继承于WebSite类
##############################################################################################
class Dm5Commnets(SiteComments):
    COMMENT_URL = 'http://www.dm5.com/manhua-{docurl}/p{page}'
    COMMENT_URL_PAGE = 'http://www.dm5.com/tiezi-{id}/'
    COMMENT_URL_PAGE_2 = 'http://www.dm5.com/tiezi-{id}-p{page}/'
    STEP_1 = None
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'
    STEP_4_BBS = '4_bbs'
    STEP_5_BBS = '5_bbs'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/30
    # @note：Dm5Commnets类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：Dm5Commnets入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Dm5Commnets.STEP_1:
                self.step1(params)
            elif params.step == Dm5Commnets.STEP_2_BBS:
                self.step2bbs(params)
            elif params.step == Dm5Commnets.STEP_3_BBS:
                self.step3bbs(params)
            elif params.step == Dm5Commnets.STEP_4_BBS:
                self.step4bbs(params)
            elif params.step == Dm5Commnets.STEP_5_BBS:
                self.step5bbs(params)
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
    # @date：2016/11/30
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("Dm5Commnets.STEP_1")

        # 1. 根据输入原始url, 拼出评论首页
        docurl = self.r.parse('^http://www\.dm5\.com/manhua-(.*)/', params.originalurl)[0]
        # 评论首页URL
        commentinfo_url = 'http://www.dm5.com/manhua-{docurl}'.format(docurl=docurl)
        # 论坛
        self.storeurl(commentinfo_url, params.originalurl, Dm5Commnets.STEP_2_BBS, {'docurl': docurl})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("Dm5Commnets.STEP_2")
        # 将STEP_1中的docurl传下来
        docurl = params.customized['docurl']

        comments_count = self.r.parse(ur'(\d+)个回复',params.content)[0]
        # 判断增量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)

        # 总数除以page_size，然后加1，可得到评论总页数comments_count
        pagenum = 0
        xparser = XPathUtility(params.content)
        if not xparser.xpath('//*[@class="inkk ma5"]'):
            Logger.getlogging().warning('{0}:30001'.format(params.originalurl))
            return
        pageList = xparser.xpath('//*[@id="search_fy"]/a/text()')
        if not pageList:
            pagenum = 1
        else:
            pagenum = int(pageList[-2])

        for page in range(1, pagenum + 1, 1):
            comment_url = Dm5Commnets.COMMENT_URL.format(docurl=docurl, page=page)
            self.storeurl(comment_url, params.originalurl, Dm5Commnets.STEP_3_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("Dm5Commnets.STEP_3")
        # 获取所有的评论url
        hrefs = self.r.parse(ur'href="/tiezi-(\d+)/"', params.content)
        hrefs = list(set(hrefs))
        for href in hrefs:
            comment_url = Dm5Commnets.COMMENT_URL_PAGE.format(id=href)
            self.storeurl(comment_url, params.originalurl, Dm5Commnets.STEP_4_BBS, {"id" : href})

    ##############################################################################################
    # @functions：step4bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step4bbs(self, params):
        Logger.getlogging().info("Dm5Commnets.STEP_4")
        id = params.customized['id']
        # 获取所有的评论url
        hrefs = self.r.parse(ur'/tiezi-\d+-p(\d+)/"', params.content)
        hrefs = list(set(hrefs))
        comment_url = Dm5Commnets.COMMENT_URL_PAGE.format(id=id)
        self.storeurl(comment_url, params.originalurl, Dm5Commnets.STEP_5_BBS)
        for href in hrefs:
            comment_url = Dm5Commnets.COMMENT_URL_PAGE_2.format(id=id, page=href)
            self.storeurl(comment_url, params.originalurl, Dm5Commnets.STEP_5_BBS)

    ##############################################################################################
    # @functions：step5bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step5bbs(self, params):
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        soup = BeautifulSoup(params.content, 'html.parser')
        commentsinfo = soup.select('.cpl_nrr2')
        commentstime = soup.select('.cpl_nrr1')
        comments = []

        # 获取评论
        for index in range(0, int(len(commentsinfo) -1), 1):
            # 提取时间
            cmti = CommentInfo()
            cmti.content = commentsinfo[index].get_text()
            publicTime = self.r.parse(ur'发表于 (.*)',commentstime[index].get_text().strip())[0]
            publicTime = getuniformtime(publicTime)
            if URLStorage.storeupdatetime(params.originalurl, publicTime):
                comments.append(cmti)
        # 保存获取到的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)

