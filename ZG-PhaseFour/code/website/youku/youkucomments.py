# coding=utf-8
##############################################################################################
# @file：youkucomments.py
# @author：Ninghz
# @date：2016/11/21
# @note：youku视频网站获取评论的文件
##############################################################################################

import json
import traceback
import time
import datetime
from utility.md5 import MD5
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
import re
##############################################################################################
# @class：YoukuComments
# @author：Ninghz
# @date：2016/11/21
# @note：youku视频网站获取评论的类，继承于SiteComments类
##############################################################################################
class YoukuComments(SiteComments):
    COMMENTS_URL = 'http://p.comments.youku.com/ycp/comment/pc/commentList?objectId=%s&app=100-DDwODVkv' \
                   '&currentPage=%d&pageSize=%d&listType=0&sign=%s&time=%s'
    PLAYINFO_URL = 'http://v.youku.com/action/getVideoPlayInfo?vid={vid}&param%5B%5D=updown&callback=data'
    PAGE_SIZE = 30
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/09/07
    # @note：youkuComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/09/07
    # @note：Step1：通过共通模块传入的html内容获取到oid，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is YoukuComments.STEP_1:
                # 从url中获取拼接评论url的参数
                objectId = self.r.getid('videoId', params.content, '\s*:\s*"')
                pTime = str(int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now()))*1000))
                #获取参数中的随机数
                sign = MD5().m('100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&'+pTime)
                # 拼接第一页评论url
                comments_url = YoukuComments.COMMENTS_URL % (objectId, 1, YoukuComments.PAGE_SIZE, sign, pTime)
                #通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, YoukuComments.STEP_2, {'objectId': objectId})

                # 来疯吧直播播放量
                if self.r.search(r'^http://v\.laifeng\.com/\d+', params.originalurl):
                    clicknum = int(self.r.getid('onlineNum', params.content))
                    NewsStorage.setclicknum(params.originalurl, clicknum)

                if objectId :
                    playinfo_url = YoukuComments.PLAYINFO_URL.format(vid=objectId)
                    self.storeurl(playinfo_url, params.originalurl, YoukuComments.STEP_2,{'objectId': objectId})
            #获取第一页评论内容，循环获取全部评论url
            elif params.step == YoukuComments.STEP_2:
                if re.findall('getVideoPlayInfo\?vid',params.url):
                    playinfo = json.loads((params.content)[20:-2])
                    clicknum = int(playinfo['data']['stat']['vv'].replace(',',''))
                    votenum = int(playinfo['data']['updown']['up'].replace(',',''))
                    NewsStorage.setclicknum(params.originalurl, clicknum)
                    NewsStorage.setvotenum(params.originalurl, votenum)
                else:
                    objectId = params.customized['objectId']
                    pTime = str(int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now()))*1000))
                    # 获取参数中的随机数
                    sign = MD5().m('100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&' + pTime)
                    # 获取评论的Jason返回值
                    comments = json.loads(params.content)
                    # 比较上次抓取该url的页面评论量和当前取到的评论量
                    if not comments.has_key('data'):
                        Logger.getlogging().warning("{url}:30000 No comments!".format(url=params.originalurl))                    
                        return
                    if not comments['data']:
                        Logger.getlogging().warning("{url}:30000 No comments!".format(url=params.originalurl))                                        
                        return

                    # 判断增量
                    comments_count = comments['data']['totalSize']
                    cmtnum = CMTStorage.getcount(params.originalurl, True)
                    if int(comments_count <= cmtnum):
                        return
                    NewsStorage.setcmtnum(params.originalurl, comments_count)

                    # 获取评论总页数
                    comments_pages = int(comments['data']['totalPage'])
                    if comments_pages == 0:
                        return
                    # 如果评论数量过多只取前十页
                    if comments_pages >= self.maxpages:
                        comments_pages= self.maxpages

                    lasttime = CMTStorage.getlastpublish(params.originalurl, True)
                    # 循环拼接评论url，提交下载平台获取评论数据
                    for page in range(0, comments_pages + 1, 1):
                        commentUrl = YoukuComments.COMMENTS_URL % (objectId, page + 1, YoukuComments.PAGE_SIZE, sign, pTime)
                        self.storeurl(commentUrl, params.originalurl, YoukuComments.STEP_3, {'objectId': objectId})

                    NewsStorage.setcmtnum(params.originalurl, int(comments['data']['totalSize']))

            #解析评论数据
            elif params.step == YoukuComments.STEP_3:
                commentsinfo = json.loads(params.content)
                for comment in commentsinfo['data']['comment']:
                    content = str(comment['content'])
                    curtime = TimeUtility.getuniformtime(int(comment['createTime']))
                    nick = comment['user']['userName']
                    # 通过时间判断评论增量
                    # if curtime > lasttime:
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                     CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()
