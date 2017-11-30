# encoding=utf-8
##############################################################################################
# @file：ThepaperComment.py
# @author：Ninghz
# @date：2016/12/8
# @note：澎湃app获取评论的文件
##############################################################################################
import time
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments

from bs4 import BeautifulSoup
from utility.gettimeutil import getuniformtime
from log.spiderlog import Logger
import re
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
##############################################################################################
# @class：ThepaperComments
# @author：Ninghz
# @date：2016/12/8
# @note：澎湃app获取评论的类，继承于SiteComments类
#       初始评论从url中查找contid,拼接评论url，后续评论url需要传递contid，热点评论id及最后一条评论id
##############################################################################################

class ThepaperComments(SiteComments):
    SOURCE_COMMENTS_URL = 'http://www.thepaper.cn/newDetail_commt.jsp?contid={contid}'
    COMMENTS_URL = 'http://www.thepaper.cn/load_newDetail_moreCommt.jsp?contid={contid}&hotIds={hotIds}&startId={startId}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Ninghz
    # @date：2016/12/8
    # @note：Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.r = RegexUtility()

    # 执行方法
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Ninghz
    # @date：2016/12/8
    # @note：Step1：通过共通模块传入的html内容获取到operaId，contentId，拼出获取评论总页数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总页数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is ThepaperComments.STEP_1:
                # 根据url获取拼接评论的参数
                contid = params.originalurl.split('_')
                contid = contid[-1]
                # 拼接初始评论url
                comments_url = ThepaperComments.SOURCE_COMMENTS_URL.format(contid=contid)
                # 通知下载平台，根据评论url获取第一页评论内容
                self.storeurl(comments_url, params.originalurl, ThepaperComments.STEP_2, {'contid': contid})
            
            elif params.step == ThepaperComments.STEP_2:
                contid = params.customized['contid']
                soup = BeautifulSoup(params.content,'html5lib')
                divs = soup.find_all(attrs={'id': re.compile('comment'), 'class': 'comment_que'})
                if not divs:
                    return

                if self.r.search(ur'startId=(.*)',params.url):
                    for index in range(1, len(divs), 1):
                        tm = divs[index].select_one('.aqwright > h3 > span').get_text()
                        curtime = getuniformtime(tm)
                        content = divs[index].select_one('.aqwright > .ansright_cont > a').get_text()
                        nick = divs[index].select_one('.aqwright > h3  > a').get_text()
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)

                else:
                    for index in range(0, len(divs), 1):
                        tm = divs[index].select_one('.aqwright > h3 > span').get_text()
                        curtime = getuniformtime(tm)
                        content = divs[index].select_one('.aqwright > .ansright_cont > a').get_text()
                        nick = divs[index].select_one('.aqwright > h3  > a').get_text()

                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)

                if self.r.search(ur'startId=(.*)',params.url):
                    hotIds = params.customized['hotIds']
                else:
                    if len(divs) > 5:
                        hotIds = self.r.parse('\d+', divs[0].get('id'))[0]
                        hotIds = hotIds + ',' + self.r.parse('\d+', divs[1].get('id'))[0]
                        hotIds = hotIds + ',' + self.r.parse('\d+', divs[2].get('id'))[0]
                        hotIds = hotIds + ',' + self.r.parse('\d+', divs[3].get('id'))[0]
                        hotIds = hotIds + ',' + self.r.parse('\d+', divs[4].get('id'))[0]
                    else:
                        hotIds = ''

                if len(divs) > 1:
                    startId = self.r.parse('\d+', divs[len(divs) - 1].get('id'))[0]
                    if not startId:
                        return
                    url = ThepaperComments.COMMENTS_URL.format(contid=contid, hotIds =hotIds ,startId=startId)
                    self.storeurl(url, params.originalurl, ThepaperComments.STEP_2, {'contid': contid, 'hotIds': hotIds})
        except:
            Logger.printexception()