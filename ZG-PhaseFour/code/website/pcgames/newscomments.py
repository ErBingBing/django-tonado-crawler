# coding=utf-8

##############################################################################################
# @file：newscomments.py
# @author：Hedian
# @date：2016/12/30
# @version：Ver0.0.0.100
# @note：太平洋游戏（PCG）新闻获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql,修改评论的获取方式

##############################################################r################################
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
import math
from lxml import etree
import json


##############################################################################################
# @class：NewsComments
# @author：Hedian
# @date：2016/12/30
# @note：太平洋游戏（PCG）新闻获取评论的类，继承于SiteComments类
##############################################################################################
class NewsComments(SiteComments):
    # SY_COMMENTS_URL = 'http://cmt.pcgames.com.cn/action/topic/get_data.jsp?url={oriurl}'
    SY_COMMENTS_URL = 'http://cmt.pcgames.com.cn/action/comment/list_new_json.jsp?url={oriurl}&pageSize={pageSize}&pageNo={page}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    limit = 10
    PAGESIZE = 20

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
    # @date：2016/12/30
    # @note：Step1：通过共通模块传入的原始url获取到Key，拼出获取评论首页的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取其他评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):

        try:
            if params.step is NewsComments.STEP_1:
                #Step1: 通过原始url得到Key，得到评论总数和指向评论的url
                comments_url = self.SY_COMMENTS_URL.format(oriurl=params.originalurl, pageSize=self.PAGESIZE,
                                                               page=1)
                #获取正文
                html = XPathUtility(params.content)
                body = html.getstring('//*[@class="article-content"]//p/text()')
                if body:
                    NewsStorage.setbody(params.originalurl, body)
                else:
                    Logger.getlogging().debug('Maybe no content for {url}!'.format(url=params.originalurl))
                self.storeurl(comments_url, params.originalurl, self.STEP_2)

            elif params.step == NewsComments.STEP_2:
                try:
                    jsondata = json.loads(params.content)
                    if 'total' in jsondata:
                        comments_count = jsondata['total']
                        NewsStorage.setcmtnum(params.originalurl, comments_count)
                        # 判断增量
                        cmtnum = CMTStorage.getcount(params.originalurl, True)
                        if cmtnum >= comments_count:
                            return
                        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGESIZE))
                        if page_num >= self.maxpages:
                            page_num = self.maxpages
                        for page in range(1, page_num + 1, 1):
                            if page == 1:
                                self.geturlcomments(params)
                                continue
                            comments_url = self.SY_COMMENTS_URL.format(oriurl=params.originalurl,
                                                                           pageSize=self.PAGESIZE, page=page)
                            self.storeurl(comments_url, params.originalurl, self.STEP_3,
                                          { 'total': comments_count})
                    else:
                        Logger.getlogging().warning('{0}:30000'.format(params.originalurl))
                except:
                    Logger.getlogging().error('{0}:30000'.format(params.originalurl))
                    Logger.printexception()
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
    # @date：2016/12/30
    # @note：保存获取的评论。
    ##############################################################################################
    def geturlcomments(self, params):
        # 获取具体评论
        try:
            jsondata = json.loads(params.content)
            if jsondata['data']:
                for comment in jsondata['data']:
                    content = comment['content']
                    curtime = TimeUtility.getuniformtime(comment['createTime'])
                    nick = comment['nickName']
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()





        #
        # xparser = XPathUtility(params.content)
        # comments_xpath = xparser.xpath('//*[@class="commentContent"]')
        # if not comments_xpath:
        #     return
        #
        # # 获取发布时间 :reply(this, '7', '侠客行', '12-28 10:09:13')
        # ip_pubtimes_xpath = xparser.xpath('//*[@class="cmtOperate"]/a[1]/@onclick')
        #
        # # 正常情况下，第一条xpath评论不是真正的评论，所以发布时间的数量比xpath的评论数少1
        # if len(comments_xpath) >= len(ip_pubtimes_xpath):
        #     comments = []
        #     # 获取评论 (正常情况下，第一条xpath评论不是真正的评论）
        #     start = len(comments_xpath) - len(ip_pubtimes_xpath)
        #     for index in range(start, len(comments_xpath), 1):
        #         content = (comments_xpath[index].text).strip().replace('\t','').replace('\n','').replace('\r','')
        #         curtime = TimeUtility.getuniformtime(ip_pubtimes_xpath[index-start])
        #         try:
        #             nick =str(ip_pubtimes_xpath[index]).split(',')[2][2:-1]
        #         except:
        #             nick = 'nickname'
        #         if not CMTStorage.exist(params.originalurl, content, curtime, nick):
        #             CMTStorage.storecmt(params.originalurl, content, curtime, nick)





