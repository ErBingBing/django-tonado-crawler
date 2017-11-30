# encoding=utf8
##############################################################################################
# @file：dm78newscomments.py
# @author：Liyanrui
# @date：2016/12/10
# @version：Ver0.0.0.100
# @note：78DM新闻页获取评论的文件
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
from bs4 import BeautifulSoup
from utility.timeutility import TimeUtility
from utility.xpathutil import XPathUtility

##############################################################################################
# @class：dm78NewsComments
# @author：Liyanrui
# @date：2016/12/10
# @note：78DM新闻页获取评论的类，继承于WebSite类
##############################################################################################
class dm78NewsComments(SiteComments):
    COMMENT_URL ='http://acg.78dm.net/comment/threads/ct/{urlId}/{page}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/12/10
    # @note：78DM新闻页类的构造器，初始化内部变量
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
    # @author：Liyanrui
    # @date：2016/12/10
    # @note：Step1：通过共通模块传入的html内容获取到urlId,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is dm78NewsComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                urlId = self.r.parse('http://acg\.78dm\.net/ct/(\d+)\.html', params.originalurl)[0]

                # 评论首页url
                comment_url = dm78NewsComments.COMMENT_URL.format(urlId=urlId, page='all/0')
                self.storeurl(comment_url, params.originalurl, dm78NewsComments.STEP_3, {'urlId': urlId, 'pagenum': 1})
            elif params.step == dm78NewsComments.STEP_3:
                # Step3: 通过Step1设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                urlId = params.customized['urlId']
                xparser = XPathUtility(params.content)
                # 取得评论
                soup = BeautifulSoup(params.content, 'html.parser')
                comments = soup.select('.commnet_ctcon')
                if not comments:
                    return
                # 取得评论时间
                temptimelist = []
                for comment in comments:
                    try:
                        curtime = comment.select_one('.commnet_time').get_text()
                        content = comment.select_one('.commnet_info').get_text()
                        nick    = comment.select_one('.commnet_cttitle').get_text()
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                        temptimelist.append(TimeUtility.getuniformtime(curtime))
                    except:
                        Logger.printexception()
                cmtnum = CMTStorage.getcount(params.originalurl)
                NewsStorage.setcmtnum(params.originalurl, cmtnum)                
                if not self.isnewesttime(params.originalurl, min(temptimelist)):
                    return
                # 生成下一页url
                page = self.r.parse('http://acg\.78dm\.net/comment/threads/ct/\d+/(.*)', params.url)[0]
                # 获取下一页评论url
                page = int(self.r.parse('http://acg\.78dm\.net/comment/threads/ct/\d+/all/(\d+)', params.url)[0]) + 10
                page = 'all/' + str(page)
                comment_url = dm78NewsComments.COMMENT_URL.format(urlId=urlId, page=page)
                pagenum = params.customized['pagenum'] + 1
                if pagenum > self.maxpages:
                    return

                self.storeurl(comment_url, params.originalurl, dm78NewsComments.STEP_3, {'urlId': urlId, 'pagenum':pagenum})
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except:
            Logger.printexception()