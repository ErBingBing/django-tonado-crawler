# encoding=utf-8

##############################################################################################
# @file：maoyancomments.py
# @author：Yongjicao
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：猫眼电影获取评论的文件
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################r################################

import json
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from bs4 import BeautifulSoup
from utility.gettimeutil import getuniformtime

##############################################################################################
# @class：MaoYan
# @author：Yongjicao
# @date：2016/12/12
# @note：猫眼电影获取评论的类，继承于WebSite类
##############################################################################################
class MaoYanComments(SiteComments):
    COMMENTS_URL = 'http://maoyan.com/ajax/news/{id}/comments?limit=10&offset={offset}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    DEFAULT_LIMIT = 10
    DEFAULT_OFFSET = 0

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/12/12
    # @note：MaoYan类的构造器，初始化内部变量
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
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is MaoYanComments.STEP_1:
                # Step1: 通过得到docurl，得到获取评论的首页url参数。
                if self.r.search('http://maoyan.com/\w+/\w+/(\d+).*', params.originalurl):
                    id = self.r.parse('http://maoyan.com/\w+/\w+/(\d+).*', params.originalurl)[0]

                    # 取得评论的url列表
                    comments_url = MaoYanComments.COMMENTS_URL.format(id=id, offset=MaoYanComments.DEFAULT_OFFSET)
                    self.storeurl(comments_url, params.originalurl, MaoYanComments.STEP_3,
                                  {'id': id, 'offset': MaoYanComments.DEFAULT_OFFSET})

                elif self.r.search('http://maoyan.com/\w+/(\d+).*', params.originalurl):
                    soup = BeautifulSoup(params.content, 'html5lib')
                    comments = soup.select('.comment-content')
                    commentTimes = soup.select('.time')
                    nicks = soup.select('span.name')
                    # commentsInfo = []
                    for index in range(0, int(len(comments)), 1):
                        # 提取时间
                        curtime = TimeUtility.getuniformtime(str(commentTimes[index]))
                        content = comments[index].get_text()
                        nick = nicks[index].get_text()
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                    # 获取数据库中评论总数,赋值给cmtnum
                    daocmtnum = CMTStorage.getcount(params.originalurl, True)
                    NewsStorage.setcmtnum(params.originalurl, daocmtnum)
                    #     if URLStorage.storeupdatetime(params.originalurl, tm):
                    #         cmti = CommentInfo()
                    #         cmti.content = comments[index].get_text()
                    #         commentsInfo.append(cmti)
                    #         # 保存获取的评论
                    # if len(commentsInfo) > 0:
                    #     self.commentstorage.store(params.originalurl, commentsInfo)

            elif params.step == MaoYanComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                id = params.customized['id']
                offset = params.customized['offset']
                jsondata = json.loads(params.content)
                dataarr = jsondata['data']['comments']
                if len(dataarr)==0:
                    return
                commentsInfo = []
                # 取得所有评论
                for index in range(0, int(len(dataarr)), 1):
                    # 提取时间
                    publicTime = dataarr[index]['created']
                    # cmti = CommentInfo()
                    curtime = TimeUtility.getuniformtime(publicTime)
                    content = dataarr[index]['text'].strip()
                    nick = dataarr[index]['author']['nickName']
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                #     if URLStorage.storeupdatetime(params.originalurl, tm):
                #         cmti.content = dataarr[index]['text'].strip()
                #         commentsInfo.append(cmti)
                #         # 保存获取的评论
                # if len(commentsInfo) > 0:
                #     self.commentstorage.store(params.originalurl, commentsInfo)
                offset +=10
                comments_url = MaoYanComments.COMMENTS_URL.format(id = id, offset = offset)
                self.storeurl(comments_url, params.originalurl, MaoYanComments.STEP_3, {'id': id,'offset':offset})

                # 获取数据库中评论总数,赋值给cmtnum
                daocmtnum = CMTStorage.getcount(params.originalurl, True)
                NewsStorage.setcmtnum(params.originalurl, daocmtnum)

            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
        except Exception, e:
            traceback.print_exc()