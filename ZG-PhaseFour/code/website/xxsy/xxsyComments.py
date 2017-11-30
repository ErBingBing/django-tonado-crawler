# encoding=utf8

##############################################################################################
# @file：XxsyComments.py
# @author：Yongjicao
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：潇湘书院新闻页获取评论的文件
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from storage.urlsstorage import URLStorage
from bs4 import BeautifulSoup

##############################################################################################
# @class：XxsyComments
# @author：Yongjicao
# @date：2016/12/12
# @note：潇湘书院新闻页获取评论的类，继承于WebSite类
##############################################################################################
class XxsyComments(SiteComments):
    FIRST_COMMENT_URL = 'http://www.xxsy.net/inc/ajax/bookComment.asp?gogo=getComment&pageid={pageid}&bookid={bookid}'
    COMMENT_URL ='http://www.xxsy.net/inc/ajax/bookComment.asp?gogo=getComment&bookid={bookid}&lastid={lastid}&pageid={pageid}'
    PAGE_SIZE = 15
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/12/012
    # @note：潇湘书院新闻页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Yongjicao
    # @date：2016/12/12
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is XxsyComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                bookid = self.r.parse('http://\w+\.xxsy\.net/\w+/(\d+).*', params.originalurl)[0]

                # 取得评论的url列表
                comments_url = XxsyComments.FIRST_COMMENT_URL.format (bookid = bookid,pageid = 1)
                self.storeurl(comments_url, params.originalurl, XxsyComments.STEP_3, {'bookid': bookid})

            elif params.step == XxsyComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                bookid = params.customized['bookid']
                if self.r.search('<input type=hidden id=nextid_p_\d+_(\d)+ value=(.*)/>', params.content):
                    arrstr = self.r.parse('<input type=hidden id=nextid_p_\d+_(\d)+ value=(.*)/>', params.content)[0]
                    if arrstr is not None:
                        pageid = int(arrstr[0])
                        lastidstr = arrstr[1][1:-2].split(',')
                        lastid = int(lastidstr[0])
                        count = int(lastidstr[1])
                    if count == 0:
                        return
                    # 取得所有评论
                    soup = BeautifulSoup(params.content, 'html5lib')
                    results = soup.find_all('div','discuss_content')
                    commentsInfo = []
                    for result in results:
                        publicTime = result.find('span', 'time').get_text()
                        publicTime = publicTime.split(']')[0][1:]
                        tm = TimeUtility.getuniformtime(TimeUtility.getuniformtime(publicTime,TimeUtility.DATE_FORMAT_DEFAULT))
                        if URLStorage.storeupdatetime(params.originalurl, tm):
                            cmti = CommentInfo()
                            cmti.content = result.find('div', 'comment').get_text().strip()
                            commentsInfo.append(cmti)
                    # 保存获取的评论
                    if len(commentsInfo) > 0:
                        self.commentstorage.store(params.originalurl, commentsInfo)

                    if count == XxsyComments.PAGE_SIZE:
                       pageid += 1

                    comments_url = XxsyComments.COMMENT_URL.format(bookid=bookid, pageid=pageid, lastid=lastid)
                    self.storeurl(comments_url, params.originalurl, XxsyComments.STEP_3, {'pageid': pageid, 'count': count,'bookid':bookid})
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except Exception,e:
            traceback.print_exc()