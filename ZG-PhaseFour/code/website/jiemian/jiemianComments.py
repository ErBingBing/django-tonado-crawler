# encoding=utf-8
##############################################################################################
# @file：jiemianComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：界面获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################
import math
import re
from website.common.comments import SiteComments
#from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
#from storage.urlsstorage import URLStorage
from utility.gettimeutil import getuniformtime
import traceback
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup

##############################################################################################
# @class：jiemianComments
# @author：Liyanrui
# @date：2016/11/18
# @note：界面获取评论的类，继承于SiteComments类
##############################################################################################
class jiemianComments(SiteComments):
    COMMENTS_URL = 'http://a.jiemian.com/index.php?m=comment&a=getlistCommentP&aid=%s&page=%d'
    PAGE_SIZE = 10
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：界面类的构造器，初始化内部变量
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
    # @date：2016/11/18
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is jiemianComments.STEP_1:
                # 取得url中的id
                articleId = re.findall(r'^http://www\.jiemian\.com/\w+/(\d+)', proparam.url).__getitem__(0)
                # 设置clicknum
                self.setclick(proparam)
                # 取得评论个数
                comments_count = float(re.findall(r'"comment_count">(\d+)</span>', proparam.content).__getitem__(0))
                if comments_count:
                    NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                # 取得评论件数
                if int(comments_count) == 0:
                    return

                # 增量判断
                cmtnum = CMTStorage.getcount(proparam.originalurl, True)
                if cmtnum >= comments_count:
                    return
                page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages
                # 循环取得评论的url
                for page in range(1, page_num + 1, 1):
                    url = jiemianComments.COMMENTS_URL % (articleId, page)
                    self.storeurl(url, proparam.originalurl, jiemianComments.STEP_3)
            elif proparam.step == jiemianComments.STEP_3:
                # proparam.content = proparam.content.replace('\\','')
                # soup = BeautifulSoup(proparam.content, 'html5lib')
                # items = soup.select('.comment-post')
                # for item in items:
                #     content = item.select_one('.comment-main > p').get_text().encode('utf-8')
                #     curtime = TimeUtility.getuniformtime(item.select_one('.date').get_text())
                #     nick = item.select_one('.author-name').get_text().decode('utf-8').encode('utf-8')
                # 取得点赞数
                votenum = self.r.getid('ding', proparam.content)
                if votenum == '':
                    Logger.getlogging().debug("Unable to get playcount")
                else:
                    NewsStorage.setvotenum(proparam.originalurl, votenum)
                # 取得评论的正则表达式
                comments = re.findall(r'<p>(.+?)<\\/p>', proparam.content)
                ctime = re.findall(r'<span class=\\"date\\">(.+?)<\\/span>',proparam.content)
                nicks = re.findall(r'class=\\"author-name\\">(.+?)<\\/a>', proparam.content)

                # 取得评论
                for index in range(0,len(comments)):
                    time = ctime[index].replace('\\', '')
                    curtime = TimeUtility.getuniformtime(time)
                    content = eval('u"' + comments[index] + '"').encode('utf-8')
                    nick = eval('u"' + nicks[index] + '"').encode('utf-8')
                    if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)


        except Exception, e:
            traceback.print_exc()
    def getcontents(self,proparam):
        # 取得评论的正则表达式
        comments = re.findall(r'<p>(.+?)<\\/p>', proparam.content)
        ctime = re.findall(r'<span class=\\"date\\">(.+?)<\\/span>', proparam.content)
        nicks = re.findall(r'class=\\"author-name\\">(.+?)<\\/a>', proparam.content)
        # 取得评论
        index = 0
        for index in range(0, len(comments)):
            time = getuniformtime(eval('u"' + ctime[index] + '"'))
            curtime = TimeUtility.getuniformtime(ctime)
            content = eval('u"' + comments[index] + '"').encode('utf-8')
            nick = eval('u"' + nicks[index] + '"').encode('utf-8')
            if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)

    def setclick(self, proparam):
        try:
            clicknum = str(re.findall(r'"jm-icon icon-a-collect"></i><span>(.*?)</span>', proparam.content))
            clicknum = self.str2num(clicknum)
            Logger.getlogging().debug('{url} clicknum:{clicknum}'.format(url=proparam.originalurl, clicknum=clicknum))
            NewsStorage.setclicknum(proparam.originalurl, clicknum)
        except:
             Logger.printexception()

    UNITS = {u'万': 10000, u'亿': 100000000, u'W': 10000}
    def str2num(self, value):
        value = value.replace('.', '')
        multiplier = 1
        for unit in self.UNITS.keys():
            if unit in value:
                 multiplier = self.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
             res = float(values[0]) * multiplier
        return int(res)
