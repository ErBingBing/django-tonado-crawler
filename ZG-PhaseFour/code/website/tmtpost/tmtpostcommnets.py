# encoding=utf8

##############################################################################################
# @file：Tmtpostcommnets.py
# @author：YuXiaoye
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################

import json
import math
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility
from utility import gettimeutil 

##############################################################################################
# @class：Tmtpostcommnets
# @author：YuXiaoye
# @date：2016/12/2
# @version：Ver0.0.0.100
# @note：钛媒体钛极客页获取评论的文件
##############################################################################################
class Tmtpostcommnets(SiteComments):
    COMMENT_URL = 'http://www.tmtpost.com/ajax/common/get?url=%2Fv1%2Fcomments%2Flist%2F{tid}&data=orderby%3D%27mixed%27%26limit%3D{limit}%26offset%3D{offset}%26avatar_size%3D%27%5B%2280_80%22%5D%27'
    STEP_1 = None
    STEP_2_BBS = '2'
    STEP_3_BBS = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：Tmtpostcommnets类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.offset = 0
        self.limit = 10

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：Tmtpostcommnets，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Tmtpostcommnets.STEP_1:
                self.step1(params)
            elif params.step == Tmtpostcommnets.STEP_2_BBS:
                self.step2bbs(params)
            elif params.step == Tmtpostcommnets.STEP_3_BBS:
                self.step3bbs(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("Tmtpostcommnets.STEP_1")
        tid = self.r.parse('^http://www.tmtpost.com/(\d+)\.html', params.originalurl)[0]
        # 1. 根据输入原始url, 拼出评论首页
        commentinfo_url = Tmtpostcommnets.COMMENT_URL.format(tid=tid, limit=self.limit, offset=self.offset)
        self.storeurl(commentinfo_url, params.originalurl, Tmtpostcommnets.STEP_2_BBS,{'tid':tid})

    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self,params):
        Logger.getlogging().info("Tmtpostcommnets.STEP_2")
        tid = params.customized['tid']
        commentsinfo = json.loads(params.content)
        comments_count = commentsinfo['cursor']['total']

        # 保存页面评论量
        cmtnum = URLStorage.getcmtnum(params.originalurl)
        if cmtnum >= comments_count:
            return
        URLStorage.setcmtnum(params.originalurl, comments_count)
        for index in range(0, int(math.ceil(float(comments_count) / self.limit)), 1):
            self.offset = index * self.limit
            commentinfo_url = Tmtpostcommnets.COMMENT_URL.format(tid=tid, limit=self.limit, offset=self.offset)
            self.storeurl(commentinfo_url, params.originalurl, Tmtpostcommnets.STEP_3_BBS)

    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/2
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("Tmtpostcommnets.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        commentsinfo = json.loads(params.content)
        comments = []

        #for index in range(0, int(len(commentsinfo['data'])), 1):
            ## 提取时间
            #cmti = CommentInfo()
            #cmti.content = commentsinfo['data'][index]['comment']
            #tm = TimeUtility.getuniformtime(commentsinfo['data'][index]['time_created'], u'%Y-%m-%d %H:%M')
            #if URLStorage.storeupdatetime(params.originalurl, tm):
                #comments.append(cmti)
                
        jsondata = commentsinfo['data']
        if not jsondata:
            return
        for data in jsondata:
            cmti = CommentInfo()
            cmti.content = data['comment']
            tm = gettimeutil.getuniformtime(data['time_created'])
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)
                

        # 保存获取的评论
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)
