# encoding=utf-8
##############################################################################################
# @file：qidiancomments.py
# @author：Merlin.W.OUYANG
# @date：2016/12/9
# @note：评论获取,起点，云中书城，起点手机，起点女生可以通用这个
##############################################################################################

from utility.gettimeutil import getuniformtime 
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from log.spiderlog import Logger
import traceback
import math
import re
from lxml import etree
from bs4 import BeautifulSoup

##############################################################################################
# @class：QidianComments
# @author：Merlin.W.OUYANG
# @date：2016/12/9
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class QidianComments(SiteComments):
    COMMENTS_URL = 'http://forum.qidian.com/NewForum/List.aspx?BookId=%s&pageIndex=%s'
    COMMENTS_URL_PAGE = 'http://forum.qidian.com/index/%d?type=1&page=%d'
    subcomments_url='http://forum.qidian.com/NewForum/%s'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4
    PAGE_SIZE = 50

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/12/9
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    #----------------------------------------------------------------------
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Merlin.W.ouyang
    # @date：2016/12/9
    # @note：Step1：通过传进来的页面获得bookid，之后获得新的地址，
    #        Step2：拿到html页面，然后读取页面内容
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is QidianComments.STEP_1:
                field = self.r.parse(r'^http://\w+\.(\w+)\.com*', params.url)[0]
                if field == 'yuncheng':
                    html=etree.HTML(params.content)
                    bookid=html.xpath('//div[@class="operatebtn"]/ul/li/a/@href')[0]
                    bookid=self.r.parse('\d+',bookid)[0]
                else:
                    bookid=self.r.parse('\d+',params.url)[0]
                comments_url = QidianComments.COMMENTS_URL % (bookid, '1')
                self.storeurl(comments_url, params.originalurl, QidianComments.STEP_3,
                              {'bookid':bookid, 
                               'pageno':'1'})
                if self.r.search('http[s]{0,1}://.*\.qidian\.com/info/.*',params.originalurl):
                    # 修正clicknum
                    if self.r.search('class=\"book-info \"', params.content):
                        soup = BeautifulSoup(params.content, 'html5lib')
                        clicknumstr = str(soup.select('div.book-info p em')[1])
                        clicknumstr = clicknumstr[4:-5]
                        if self.r.search('\.', clicknumstr):
                            clicknum = self.str2num(clicknumstr+'万')
                            NewsStorage.setclicknum(params.originalurl, clicknum)
                        else:
                            clicknum = clicknumstr
                            NewsStorage.setclicknum(params.originalurl,clicknum)

            elif params.step is QidianComments.STEP_3:
                # html=etree.HTML(params.content)
                threadid = int(self.r.parse(ur'forumId = \'(.*?)\'',params.content)[0])
                comment_counts = self.r.parse(ur'class="nav-tab.*act">全部(.*?)</a>',params.content)[0].strip()
                comment_counts = int(comment_counts[1:-1])
                # 设置cmtnum
                if comment_counts:
                    NewsStorage.setcmtnum(params.originalurl, comment_counts)
                    # 判断增量
                    cmtnum = CMTStorage.getcount(params.originalurl, True)
                    if cmtnum >= comment_counts:
                        return
                    page_num = int(math.ceil(float(comment_counts - cmtnum) / self.PAGE_SIZE))
                    if page_num >= self.maxpages:
                        page_num = self.maxpages

                    for page in range(1, page_num + 1, 1):
                        if page == 1:
                            self.getcontents(params)
                            continue
                        commentUrl = QidianComments.COMMENTS_URL_PAGE % (threadid, page)
                        self.storeurl(commentUrl, params.originalurl, QidianComments.STEP_4)


            elif params.step is QidianComments.STEP_4:
                self.getcontents(params)

        except Exception, e:
            Logger.printexception()

    def getcontents(self,params):
        soup = BeautifulSoup(params.content, 'html5lib')
        lis = soup.select('.all-post > .post-wrap')
        for li in lis:
            content = li.select_one('.post-body > a').get_text()
            curtime = li.select_one('.mr20').get_text()
            nick = li.select_one('.post-auther > a').get_text()
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

    UNITS = {u'万': 10000, u'亿': 100000000}

    def str2num(self, value):
        value = value.replace(',', '')
        multiplier = 1
        for unit in self.UNITS.keys():
            if unit in value:
                multiplier = self.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
            res = float(values[0]) * multiplier
        return int(res)