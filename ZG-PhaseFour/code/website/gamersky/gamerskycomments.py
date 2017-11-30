# encoding=utf-8
##############################################################################################
# @file：gamerskycomments.py
# @author：Liyanrui
# @date：2016/11/17
# @version：Ver0.0.0.100
# @note：动漫星空获取评论的文件
###############################################################################################
import math
import re
import traceback
import json
from log.spiderlog import Logger
from  bs4 import BeautifulSoup 
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from utility.bbs2commom import CommenComments
from utility.gettimeutil import getuniformtime

##############################################################################################
# @class：gamerSkyComments
# @author：Liyanrui
# @date：2016/11/17
# @note：动漫星空获取评论的类，继承于SiteComments类
##############################################################################################
class GamerSkyComments(SiteComments):
    COMMENTS_URL = 'http://cm.gamersky.com/api/getcomment?jsondata={"pageIndex":%d,"pageSize":"10","articleId":"%s","isHot":false}'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    Flg = True

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/17
    # @note：动漫星空类的构造器，初始化内部变量
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
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        field = self.r.parse(r'^http://(\w+)\.gamersky\.com/.*', params.originalurl)[0]
        # 论坛网址
        if field == 'bbs':
            # 调用共通取得评论
            CommenComments.getinstance(self).process(params)
        # 新闻网址
        else:
            self.processNews(params)

    ##############################################################################################
    # @functions：processNews
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def processNews(self, params):
        #Logger.getlogging().info(params.url)
        try:
            if params.step is GamerSkyComments.STEP_1:
                # 取得url中的id
                if self.r.search('data-sid=\"(\w+)\"', params.content) is not None:
                    articleId = self.r.parse('data-sid=\"(\w+)\"', params.content)[0]
                else:
                    articleId = self.r.parse('sid=\"(\w+)\"', params.content)[0]

                # 取得评论的url列表
                comments_url = GamerSkyComments.COMMENTS_URL % (1, articleId)
                self.storeurl(comments_url, params.originalurl, GamerSkyComments.STEP_2, {'articleId': articleId})

            elif params.step == GamerSkyComments.STEP_2:
                articleId = params.customized['articleId']
                # Step2: 通过Step1设置url，得到评论的总数和当前url的评论，并根据评论总数得到获取其他评论的url。
                curcmtnum = float(self.r.parse(r'"Count\\":(\d+)', params.content)[0])
                if int(curcmtnum) == 0:
                    Logger.getlogging().info('comments count:{count}'.format(count=curcmtnum))
                    return

                # 增量判断
                dbcmtnum = CMTStorage.getcount(params.originalurl, True)
                NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
                if dbcmtnum >= curcmtnum:
                    return
                pages = int(math.ceil(float(curcmtnum-dbcmtnum)/self.PAGE_SIZE))

                # 循环取得评论的url
                for page in range(1, pages + 1, 1):
                    if page == 1:
                        self.step3(params)
                        continue
                    # 取得评论的url
                    url = GamerSkyComments.COMMENTS_URL % (page, articleId)
                    self.storeurl(url, params.originalurl, GamerSkyComments.STEP_3)

            elif params.step == GamerSkyComments.STEP_3:
                self.step3(params)

            else:
                Logger.getlogging().error("params.step == %d", params.step)

        except:
            Logger.printexception()
            
    def step3(self, params):
        try:
            left = params.content.index('(')
            right= params.content.rindex(')')
            jsondata = json.loads(params.content[left+1:right])['body']
            # 通过Step2设置url，得到评论的总数
            content = json.loads(jsondata)
            comment = content['NewComment']
            soup = BeautifulSoup(comment, 'html5lib')
            divs = soup.select('.cmt-list-cont')
            for div in divs:
                content = div.select_one('.cmt-msg-wrap > .wrap-issue').get_text()
                publictime = div.select_one('.user-time').get_text()
                CMTStorage.storecmt(params.originalurl, content, publictime, '')
        except:
            Logger.printexception()
