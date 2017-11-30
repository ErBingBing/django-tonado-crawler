# encoding=utf-8
##############################################################################################
# @file：kkkManhuaComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：极速漫画获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################
import math
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
import traceback

##############################################################################################
# @class：kkkManhuaComments
# @author：Liyanrui
# @date：2016/11/18
# @note：极速漫画获取评论的类，继承于SiteComments类
##############################################################################################
class kkkManhuaComments(SiteComments):
    COMMENTS_URL_MANHUA = 'http://www.1kkk.com/manhua%s/p%d/#topic'
    COMMENTS_URL = 'http://www.1kkk.com/%s-%s/'
    COMMENTS_URL_PAGE = 'http://www.1kkk.com/%s-%s-p%d/'
    COMMENTS_URL_CH = 'http://www.1kkk.com/%s-%s-%s/'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：极速漫画类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：Step1：通过共通模块传入的html内容获取到articleIds，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is kkkManhuaComments.STEP_1:
                # 取得评论个数
                comments_count = float(self.r.parse(ur'(\d+)个回复', proparam.content).__getitem__(0))
                if comments_count:
                    NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                # 取得url中的id
                self.matchObj = self.r.search(r'^http://www\.1kkk\.com/manhua(\d+)', proparam.url)
                if self.matchObj:
                    # 取得评论件数
                    if int(comments_count) == 0:
                        return
                    # 判断增量
                    cmtnum = CMTStorage.getcount(proparam.originalurl, True)
                    if cmtnum >= comments_count:
                        return
                    page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                    if page_num >= self.maxpages:
                        page_num = self.maxpages
                    #获取评论列表参数
                    articleId1 = self.r.parse(r'^http://www\.1kkk\.com/manhua(\d+)', proparam.url)[0]
                    # #获取总页数
                    # pages = self.r.parse(ur'<a href="/manhua\d+/p\d+/#topic">(\d+)</a>', proparam.content)
                    # if len(pages) > 1:
                    #     pages = int(pages[-1])
                    # else:
                    #     pages = 1

                    # 循环取得评论的url
                    for page in range(1, page_num + 1, 1):
                        # 取得评论的url
                        url = kkkManhuaComments.COMMENTS_URL_MANHUA % (articleId1, page)
                        self.storeurl(url, proparam.originalurl, kkkManhuaComments.STEP_2)
                else:
                    # 取得评论url的前面俩个参数
                    articleIds = self.r.parse(r'^http://www\.1kkk\.com/(\w+)-(\d+)', proparam.url).__getitem__(0)

                    # 评论参数1
                    articleId1 = articleIds.__getitem__(0)
                    # 评论参数2
                    articleId2 = articleIds.__getitem__(1)

                    url = kkkManhuaComments.COMMENTS_URL_CH % (articleId1, articleId2, 'pl1')
                    self.storeurl(url, proparam.originalurl, kkkManhuaComments.STEP_4,
                                  {'articleId1': articleId1, 'articleId2': articleId2})

                    hrefs = self.r.parse(ur'<a href="/ch\d+-\d+-pl(\d+)/#topl">', proparam.content)
                    if len(hrefs) > 1:
                        pages = int(hrefs[-2])

                        # 循环取得评论的url
                        for page in range(2, pages + 1, 1):
                            # 取得评论的url
                            url = kkkManhuaComments.COMMENTS_URL_CH % (articleId1, articleId2, 'pl' + str(page))
                            self.storeurl(url, proparam.originalurl, kkkManhuaComments.STEP_4, {'articleId1':articleId1, 'articleId2':articleId2})
            elif proparam.step == kkkManhuaComments.STEP_2:
                # 取得评论url的前面俩个参数列表
                articleIds = self.r.parse(r'a href="/(\w+)-(\d+)/#topic" id="A4"', proparam.content)

                for articleId in articleIds:
                    # 评论参数1
                    articleId1 = articleId.__getitem__(0)

                    # 评论参数2
                    articleId2 = articleId.__getitem__(1)

                    # 取得评论的url
                    url = kkkManhuaComments.COMMENTS_URL % (articleId1, articleId2)
                    self.storeurl(url, proparam.originalurl, kkkManhuaComments.STEP_3,
                                  {'articleId1': articleId1, 'articleId2': articleId2})
            elif proparam.step == kkkManhuaComments.STEP_3:
                # 获取所有的评论url
                articleId1 = proparam.customized['articleId1']
                articleId2 = proparam.customized['articleId2']
                self.storeurl(proparam.url, proparam.originalurl, kkkManhuaComments.STEP_4)
                hrefs = self.r.parse(ur'/tiezi-\d+-p(\d+)/"', proparam.content)
                if len(hrefs) > 1:
                    pages = int(hrefs[-2])
                    for page in range(2, pages+1, 1):
                        url = kkkManhuaComments.COMMENTS_URL_PAGE % (articleId1, articleId2, page)
                        self.storeurl(url, proparam.originalurl, kkkManhuaComments.STEP_4)

            elif proparam.step == kkkManhuaComments.STEP_4:

                if self.matchObj:
                    # 获取评论
                    soup = BeautifulSoup(proparam.content, 'html5lib')
                    comments = soup.select('.sy_tb52_nr')
                    # 获取时间
                    commentTimes =self.r.parse(ur'发表于 (.+?)</div>', proparam.content)
                    nicks = self.r.parse(ur'id="replyuser(\d+)">(.+?)</a>',proparam.content)
                else:
                    soup = BeautifulSoup(proparam.content, 'html.parser')
                    # 获取评论
                    comments = soup.findAll('div',{'class':"sy_tb52_nr z14 mt10"})
                    # 获取时间
                    commentTimes = self.r.parse(ur'发表于 (.+?)</div>', proparam.content)
                    if not comments or not commentTimes:
                        return
                for index in range(0, int(len(comments)), 1):
                    content = str(comments[index].get_text())
                    curtime = TimeUtility.getuniformtime(commentTimes[index][0:19])
                    nick = nicks[index][1]
                    if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)

        except Exception, e:
            traceback.print_exc()