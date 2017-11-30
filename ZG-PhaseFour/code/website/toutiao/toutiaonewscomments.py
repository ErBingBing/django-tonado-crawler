# encoding=utf8

##############################################################################################
# @file：ToutiaoComments.py
# @author：QW_Liang
# @date：2017/9/138
# @version：Ver0.0.0.100
# @note：今日头条获取评论的文件
##############################################################################################

import json
import math
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from utility.httputil import HttpUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
##############################################################################################
# @class：ToutiaoNewsComments
# @author：QW_Liang
# @date：2017/9/13
# @version：Ver0.0.0.100
# @note：今日头条获取评论的文件
##############################################################################################
class ToutiaoNewsComments(SiteComments):
    # COMMENTS_URL = 'http://www.toutiao.com/api/comment/list/?group_id={0}&item_id={1}&offset={2}&count={3}'
    COMMENTS_URL = 'http://lf.snssdk.com/article/v2/tab_comments/?group_id={0}&offset={1}&count={2}'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/9/13
    # @note：ToutiaoNewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 20
        self.h = HttpUtility()

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/13
    # @note：ToutiaoComments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is ToutiaoNewsComments.STEP_1:
                self.step1(params)
            if params.step is ToutiaoNewsComments.STEP_2:
                self.step2(params)
            elif params.step == ToutiaoNewsComments.STEP_3:
                self.step3(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            # traceback.print_exc()
            Logger.printexception()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/13
    # @note：根据主页获取评论页，传入评论页，获取评论数
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("ToutiaoNewsComments.STEP_1")
        group_id = self.r.parse('http://www.toutiao.com/(\w+)/.*',params.originalurl)[0]
        if group_id:
            group_id = group_id[1:]
        # group_id = self.r.getid("groupId", params.content)
        # item_id = self.r.getid("itemId", params.content)
        # if not group_id:
        #     group_id = self.r.getid("group_id", params.content)
        #     item_id = self.r.getid("item_id", params.content)

        try:
            publishdate = self.r.getid("time", params.content)
            if not publishdate:
                publishdate = self.r.getid("publish_time", params.content)
            if publishdate:
                NewsStorage.setpublishdate(params.originalurl,publishdate)
        except:
            Logger.getlogging().error('{0}:30000'.format(params.originalurl))
        if not group_id :
            Logger.getlogging().error('{0}:30000'.format(params.originalurl))
            return

        # commentinfo_url = ToutiaoNewsComments.COMMENTS_URL.format(group_id, item_id, 1, self.page_size)
        commentinfo_url = ToutiaoNewsComments.COMMENTS_URL.format(group_id, 0, self.page_size)
        self.storeurl(commentinfo_url, params.originalurl, ToutiaoNewsComments.STEP_2,{'group_id':group_id})

    ##############################################################################################
    # @functions：step2news
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/13
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("ToutiaoNewsComments.STEP_2")
        group_id = params.customized['group_id']
        # item_id = params.customized['item_id']
        jsoncontent = json.loads(params.content)
        comments_count = jsoncontent['total_number']

        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        if cmtnum >= comments_count:
            return
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        # 判断最大页数
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.page_size))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        for index in range(0, page_num+1, 1):
            if index == 0:
                self.step3(params)
                continue
            offset = index*self.page_size
            commentinfo_url = ToutiaoNewsComments.COMMENTS_URL.format(group_id,offset,self.page_size)
            self.storeurl(commentinfo_url, params.originalurl, ToutiaoNewsComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/9/13
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("ToutiaoNewsComments.STEP_3")
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        jsoncontent = json.loads(params.content)
        if jsoncontent:
            if len(jsoncontent['data']) == 0:
                return
            for item in jsoncontent['data']:
                content = item['comment']['text']
                curtime = TimeUtility.getuniformtime(item['comment']['create_time'])
                if not CMTStorage.exist(params.originalurl, content, curtime, ''):
                    CMTStorage.storecmt(params.originalurl, content, curtime, '')

