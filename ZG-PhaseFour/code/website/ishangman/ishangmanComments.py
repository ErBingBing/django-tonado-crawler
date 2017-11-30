# encoding=utf-8
##############################################################################################
# @file：ishangmanComments.py
# @author：Liyanrui
# @date：2016/11/18
# @version：Ver0.0.0.100
# @note：i尚漫获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/12
# @note:第113,121行使用utility.gettimeutil.getuniformtime方法处理没有具体年的时间
###############################################################################################
import math
import re
import time
from website.common.comments import SiteComments
#from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
import traceback
#from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility
from utility.gettimeutil import getuniformtime
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：ishangmanComments
# @author：Liyanrui
# @date：2016/11/18
# @note：i尚漫获取评论的类，继承于SiteComments类
##############################################################################################
class ishangmanComments(SiteComments):
    COMMENTS_URL = 'http://%s.ishangman.com/comment_list.php?id=%s&type=%d&page=%d&order=new'
    PAGE_SIZE = 20.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/18
    # @note：i尚漫类的构造器，初始化内部变量
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
    # @note：Step1：通过共通模块传入的html内容获取到articleIds，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, proparam):
        Logger.getlogging().info(proparam.url)
        try:
            if proparam.step is ishangmanComments.STEP_1:
                # 取得url中的参数值
                articleIds = re.findall(r'^http://(\w+)\.ishangman\.com/\w+/(\d+)', proparam.url).__getitem__(0)
                articleId1 = articleIds.__getitem__(0)
                articleId2 = articleIds.__getitem__(1)
                # 评论类型
                commenttype = int(self.r.parse(ur'commenttype = (.*);', proparam.content)[0])
                #第一页评论
                url = ishangmanComments.COMMENTS_URL % (articleId1, articleId2, commenttype, 1)
                self.storeurl(url, proparam.originalurl, ishangmanComments.STEP_2, {'articleId1':articleId1, 'articleId2':articleId2, 'commenttype':commenttype})

            elif proparam.step == ishangmanComments.STEP_2:
                articleId1 = proparam.customized['articleId1']
                articleId2 = proparam.customized['articleId2']
                commenttype = proparam.customized['commenttype']
                # 取得评论件数
                xhtml = XPathUtility(html=proparam.content)
                if articleId1.__eq__('comic'):
                    comments_count = int(xhtml.getlist('//*[contains(@class,"ismcartondiv1")]/p/strong')[0])
                    if comments_count:
                        NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                else:
                    comments_count = int(self.r.parse(ur'(\d+).*',xhtml.getlist('//*[@class="comment_lctwidl"]/p')[0])[0])
                    if comments_count:
                        NewsStorage.setcmtnum(proparam.originalurl, comments_count)
                # 取得评论的页数
                cmtnum = CMTStorage.getcount(proparam.originalurl, True)
                if int(comments_count) == 0:
                    return
                page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages

                # 取得评论的url
                for page in range(1, page_num + 1, 1):
                    url = ishangmanComments.COMMENTS_URL % (articleId1, articleId2, commenttype, page)
                    self.storeurl(url, proparam.originalurl, ishangmanComments.STEP_3, {'articleId1': articleId1})

            elif proparam.step == ishangmanComments.STEP_3:
                try:
                    Logger.getlogging().debug(proparam.originalurl)
                    commentsInfo = []
                    articleId1 = proparam.customized['articleId1']
                    xparser = XPathUtility(proparam.content)
                    # 取得评论件数
                    if articleId1.__eq__('comic'):
                        # 论坛评论
                        soup = BeautifulSoup(proparam.content, 'html5lib')
                        comments = soup.select('.ismcartondiv2')
                    else:
                        # 论坛评论
                        comments = xparser.getcomments('/html/body/div/span[2]/p[1]')
                        # 论坛评论时间
                        updateTime = xparser.getcomments('/html/body/div/span[2]/div[1]')

                    # 取得评论
                    for index in range(0, int(len(comments)), 1):
                        cmti = []
                        if articleId1.__eq__('comic'):
                            publictime = self.r.parse(ur'(\d{2}-\d+ \d+:\d+)',comments[index].get_text())[0]
                            # publictime  = TimeUtility.getuniformtime(publictime)
                            if publictime:
                                cmt_month = publictime.split("-")[0]
                                curmonth =  time.localtime().tm_mon
                                if(int(cmt_month)<curmonth):
                                    publictime = TimeUtility.getcurrentdate()[0:4] + '-' + publictime
                                else:
                                    publictime = '2016'+ '-' + publictime
                            curtime = TimeUtility.getuniformtime(publictime)
                            content = comments[index].text.split('\n')[0].get_text()

                            # # print comments;
                            # return
                            # content = self.r.parse(ur'class=\".*\"',comments[index].get_text())[0]
                            # nick = comments[1].get('nickname', 'anonymous')
                            #
                            # if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                            #     CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
                            # if NewsStorage.storeupdatetime(proparam.originalurl, tm):
                            #     cmti.content = comments[index].get_text()
                            #     commentsInfo.append(cmti)
                        else:
                            publictime = updateTime[index][:-8]
                            #publictime = TimeUtility.getcurrentdate()[0:4] + '-'+ publictime
                            #tm = TimeUtility.getuniformtime(publictime, u'%Y-%m-%d %H:%M')
                            tm = getuniformtime(publictime)
                            if NewsStorage.storeupdatetime(proparam.originalurl, tm):
                                cmti.content = comments[index]
                                commentsInfo.append(cmti)

                        # 保存获取的评论i
                    if len(commentsInfo) > 0:
                        self.commentstorage.store(proparam.originalurl, commentsInfo)

                except:
                    Logger.printexception()
                    Logger.getlogging().error('extract comment error from {site}'.format(site=proparam.url))
            else:
                Logger.getlogging().error("proparam.step == %d", proparam.step)

        except Exception, e:
            traceback.print_exc()