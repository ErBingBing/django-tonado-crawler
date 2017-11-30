# encoding=utf8

##############################################################################################
# @file：poocgNewsComments.py
# @author：Liyanrui
# @date：2016/12/09
# @version：Ver0.0.0.100
# @note：涂鸦王国新闻页获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql

##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
import math
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup

##############################################################################################
# @class：poocgNewsComments
# @author：Liyanrui
# @date：2016/12/09
# @note：涂鸦王国新闻页获取评论的类，继承于WebSite类
##############################################################################################
class poocgNewsComments(SiteComments):
    COMMENT_URL ='http://www.poocg.com/index.php?app=works&action=view_load_comment&albumid=%s&page=%d'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/12/09
    # @note：涂鸦王国新闻页类的构造器，初始化内部变量
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
    # @date：2016/12/09
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is poocgNewsComments.STEP_1:
                #Step1: 通过得到docurl，得到获取评论的首页url参数。
                articleId = self.r.parse('^http[s]?://www\.poocg\.com/works/view/(\d+)', params.originalurl)[0]
                # 取得总件数
                comment_count = float(self.r.parse(ur'<p><strong>(\d+)</strong><span>评论</span></p>', params.content)[0])
                NewsStorage.setcmtnum(params.originalurl, int(comment_count))
                if comment_count == 0:
                    return

                # 判断增量
                cmtnum = CMTStorage.getcount(params.originalurl, True)
                if cmtnum >= comment_count:
                    return


                # 获取页数
                page_num = int(math.ceil(float(comment_count - cmtnum) / poocgNewsComments.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages
                # 获得url列表
                for page in range(1, page_num + 1, 1):
                    url = poocgNewsComments.COMMENT_URL % (articleId, page)
                    self.storeurl(url, params.originalurl, poocgNewsComments.STEP_3)

                if NewsStorage.getclicknum(params.originalurl) <= 0:
                   clicknum = int(self.r.parse(ur'<p><strong>(\d+)</strong><span>浏览</span></p>', params.content)[0])
                   NewsStorage.setpublishdate(params.originalurl, clicknum)
                if NewsStorage.getfansnum(params.originalurl) <= 0:
                    fansnum = int(self.r.parse(ur'<p><strong>(\d+)</strong><span>喜欢</span></p>', params.content)[0])
                    NewsStorage.setpublishdate(params.originalurl, fansnum)
                publishdate = str(self.r.parse(ur'<p.*class="signed">(.*?)</p>', params.content)[0])
                NewsStorage.setpublishdate(params.originalurl, TimeUtility.getuniformtime(publishdate))

            elif params.step == poocgNewsComments.STEP_3:
                # Step3: 通过Step2设置的url，得到所有评论，抽取评论
                Logger.getlogging().info("params.step == 3")
                xparser = XPathUtility(params.content)
                # 取得所有评论
                soup = BeautifulSoup(params.content, 'html.parser')
                comments = soup.select('.p2')
                nicks = soup.select('.name')
                # 取得所有评论时间
                times = soup.select('.contentbox .time')

                commentsInfo = []
                # 取得所有评论
                for index in range(0, int(len(comments)), 1):
                    # 提取时间
                    # year = TimeUtility.getcurrentdate()[0:4]
                    # publictime= year + '年' + commenttimes[index].text
                    try:
                        if len(times)>0:
                            publictime = times[index].get_text()
                            curtime = TimeUtility.getuniformtime(publictime)
                        else:
                            curtime = ''
                    except:
                        curtime =''
                    content = comments[index].get_text()
                    try:
                        nick = str(nicks[index].get_text())
                    except:
                        nick = 'nickname'
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                        #     if URLStorage.storeupdatetime(params.originalurl, tm):
                #         cmti = CommentInfo()
                #         cmti.content = comments[index].get_text()
                #         commentsInfo.append(cmti)
                #
                #     # 保存获取的评论
                # if len(commentsInfo) > 0:
                #     self.commentstorage.store(params.originalurl, commentsInfo)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except Exception,e:
            traceback.print_exc()