# encoding=utf8

##############################################################################################
# @file：MtimeComments.py
# @author：YuXiaoye
# @date：2016/12/6
# @version：Ver0.0.0.100
# @note：时光网获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：时光网获取评论的文件
##############################################################################################
import json
import math
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
from bs4 import BeautifulSoup

##############################################################################################
# @class：MtimeComments
# @author：YuXiaoye
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：时光网获取评论的文件


##############################################################################################
class MtimeComments(SiteComments):
    COMMENT_URL = 'http://service.library.mtime.com/CMS.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetCmsNewsCommentList&Ajax_CallBackArgument0={topic_id}&Ajax_CallBackArgument1={page}&Ajax_CallBackArgument3=1'
    COMMENT_URL_PEOPLE1 = 'http://people.mtime.com/{docId}/comment.html'
    COMMENT_URL_PEOPLE2 = 'http://people.mtime.com/{docId}/comment-{page}.html'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：MtimeComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/12
    # @note：MMtimeComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if self.r.search('^http://news.mtime.com/.*', params.originalurl):
                if params.step is MtimeComments.STEP_1:
                    Logger.getlogging().info("MtimeComments.STEP_1")
                    topic_id = self.r.parse('^http://news.mtime.com/\d+/\d+/\d+\/(\d+)\.html', params.originalurl)[0]
                    # 1. 根据输入原始url, 拼出评论首页
                    commentinfo_url = MtimeComments.COMMENT_URL.format(topic_id=topic_id, page=0)
                    self.storeurl(commentinfo_url, params.originalurl, MtimeComments.STEP_2, {'topic_id': topic_id})
                elif params.step == MtimeComments.STEP_2:
                    Logger.getlogging().info("MtimeComments.STEP_2")
                    topic_id = params.customized['topic_id']
                    params.content = params.content.strip()[params.content.index('{'):params.content.index(';')]
                    commentsinfo = json.loads(params.content)
                    comments_count = commentsinfo['value']['totalCount']
                    if comments_count:
                        NewsStorage.setcmtnum(params.originalurl, comments_count)
                    cmtnum = CMTStorage.getcount(params.originalurl, True)
                    # 判断增量
                    if cmtnum >= comments_count:
                        return
                    page_num = int(
                        math.ceil(float(int(commentsinfo['value']['totalCount']) - cmtnum) / float(commentsinfo['value']['pageSize'])))
                    if page_num >= self.maxpages:
                        page_num = self.maxpages
                    for index in range(1, page_num + 1, 1):
                        commentinfo_url = MtimeComments.COMMENT_URL.format(topic_id=topic_id, page=index)
                        self.storeurl(commentinfo_url, params.originalurl, MtimeComments.STEP_3)
                elif params.step == MtimeComments.STEP_3:
                    Logger.getlogging().info("MtimeComments.STEP_3")
                    # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                    params.content = params.content.strip()[params.content.index('{'):params.content.index(';')]
                    commentsinfo = json.loads(params.content)
                    # comments = []
                    # for index in range(0, int(len(commentsinfo['value']['comments'])), 1):
                    #     # 提取时间
                    #     cmti = CommentInfo()
                    #     cmti.content = commentsinfo['value']['comments'][index]['content']
                    #     tm = getuniformtime(commentsinfo['value']['comments'][index]['enterTime'])
                    #     if URLStorage.storeupdatetime(params.originalurl, tm):
                    #         comments.append(cmti)
                    # # 保存获取的评论
                    # if len(comments) > 0:
                    #     self.commentstorage.store(params.originalurl, comments)
                    for item in commentsinfo['value']['comments']:
                        content = item['content']
                        curtime = TimeUtility.getuniformtime(item['enterTime'])
                        nick = item['nickName']
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)

                else:
                    Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
                    return
            elif self.r.search('^http://people.mtime.com/.*', params.originalurl):
                if params.step is MtimeComments.STEP_1:
                    Logger.getlogging().info("MtimeComments.STEP_1")
                    cmtnum = CMTStorage.getcount(params.originalurl,True)
                    if cmtnum:
                        NewsStorage.setcmtnum(params.originalurl, cmtnum)
                    docId = self.r.parse('^http://people.mtime.com/(\d+)/', params.originalurl)[0]
                    # 1. 根据输入原始url, 拼出评论首页
                    commentinfo_url = MtimeComments.COMMENT_URL_PEOPLE1.format(docId=docId)
                    self.storeurl(commentinfo_url, params.originalurl, MtimeComments.STEP_2, {'docId': docId})
                elif params.step == MtimeComments.STEP_2:
                    Logger.getlogging().info("MtimeComments.STEP_2")
                    docId = params.customized['docId']
                    soup = BeautifulSoup(params.content, 'html5lib')
                    page = soup.select('.num')
                    self.storeurl(params.url, params.originalurl, MtimeComments.STEP_3)
                    for index in range(2, len(page) + 2, 1):
                        commentinfo_url = MtimeComments.COMMENT_URL_PEOPLE2.format(docId=docId, page=index)
                        self.storeurl(commentinfo_url, params.originalurl, MtimeComments.STEP_3)
                elif params.step == MtimeComments.STEP_3:
                    Logger.getlogging().info("MtimeComments.STEP_3")
                    # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                    soup = BeautifulSoup(params.content, 'html5lib')
                    comments = soup.select('div.mod_short')
                    commentTimes = soup.select('span.fl')
                    nicks = soup.select('p.px14')
                    # commentInfo = []
                    for index in range(0, len(comments), 1):
                           # 提取时间
                    #     cmti = CommentInfo()
                    #     cmti.content = comments[index].get_text()
                    #     tm = getuniformtime(self.r.parse(u'entertime="(.+?)"', str(commentTimes[index + 1]))[0])
                    #     if URLStorage.storeupdatetime(params.originalurl, tm):
                    #         commentInfo.append(cmti)
                    # # 保存获取的评论
                    # if len(commentInfo) > 0:
                    #     self.commentstorage.store(params.originalurl, commentInfo)
                        content = comments[index].get_text().strip().replace('\s','')
                        curtime = TimeUtility.getuniformtime((self.r.parse(u'entertime="(.+?)"', str(commentTimes[index + 1]))[0]))
                        nick = nicks[index].get_text().strip()
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                else:
                    Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
                    return
        except Exception,e:
            traceback.print_exc()