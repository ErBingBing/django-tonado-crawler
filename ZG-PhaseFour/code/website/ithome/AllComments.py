# encoding=utf-8
##############################################################################################
# @file：pcgamescomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/17
# @note：IT之家评论获取
##############################################################################################

from website.common.comments import SiteComments
# from storage.commentsstorage import CommentInfo
# from storage.urlsstorage import URLStorage
from log.spiderlog import Logger
from bs4 import BeautifulSoup
import traceback
import math
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/11/17
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    COMMENTS_URL = "http://dyn.ithome.com/ithome/getajaxdata.aspx?newsID=%s&hash=%s&type=commentpage&page=%d&order=false"
    COMMENTS_COUNTS_URL = "http://dyn.ithome.com/comment/%s"
    PAGE_SIZE = 50.0
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/17
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        #self.r = RegexUtility()
        #self.basicstorage = BaseInfoStorage()
        #self.commentstorage = CommentsStorage()
    ################################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Merlin.W.ouyang
    # @date：2016/11/17
    # @note：Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
    #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
    #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
    #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
    #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
    #################################################################################################
    def process(self, params):
        try:
            #Step 1 Start
            if params.step is AllComments.STEP_1:
                # newsid = self.r.parse('http[s]{0,1}://www\.ithome\.com/.*',params.originalurl)[0]
                newsid = self.r.parse('http[s]{0,1}://www\.ithome\.com/\w+/\w+/(\d+).htm', params.originalurl)[0]
                comement_url = AllComments.COMMENTS_COUNTS_URL % (newsid)
                self.storeurl(comement_url, params.originalurl, AllComments.STEP_2, {'newsid':newsid})

            #Step 2 Start
            elif params.step is AllComments.STEP_2:
                newsid = params.customized['newsid']
                comment_counts = int(self.r.parse('innerHTML\s*=\s*\'(\d+)\'',params.content)[0])
                # 设置cmtnum
                if comment_counts:
                    NewsStorage.setcmtnum(params.originalurl, comment_counts)
                hash = self.r.parse('id=\"hash\" value=\"(\w+)\"',params.content)[0]
                #id="hash" value="7D046EF0AACBDFD1"

                # 判断增量
                cmtnum = CMTStorage.getcount(params.originalurl, True)
                if cmtnum >= comment_counts:
                    return
                page_num = int(math.ceil(float(comment_counts - cmtnum) / self.PAGE_SIZE))
                if page_num >= self.maxpages:
                    page_num = self.maxpages

                for page in range(1, page_num +1, 1):
                    commentUrl = AllComments.COMMENTS_URL % (newsid,hash,page)
                    self.storeurl(commentUrl, params.originalurl, AllComments.STEP_3)

            #Step 3 Start
            elif params.step is AllComments.STEP_3:
                # print params.content
                soup = BeautifulSoup(params.content, 'html5lib')
                infos = soup.select(".entry")
                if infos.__len__() == 0:
                    return
                comments = []
                # 抓取评论
                for info in infos[0:]:
                    content = info.select('div.comm')[0].get_text().strip()
                    content = content.decode('utf8').encode('utf8')
                    timestr = info.select('div > span.posandtime')[0].get_text().strip()
                    curtime = self.r.parse('(\d+-\d+-\d+ \d+:\d+:\d+)', timestr)[0]
                    nick = info.select('strong.nick')[0].get_text().strip()
                    if not nick:
                        nick = nick.get('nickname', 'anonymous')
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)


                # 抓取评论的回复
                for info in infos[0:]:
                    replys = info.select('ul.reply > li')
                    if replys.__len__() > 0 and replys.__len__() <= 5:
                        self.processReply(params, replys)
                    elif replys.__len__() > 5:
                        self.processReply(params, replys[0:4])
                        replyid = self.r.parse('(\d+)', replys[5].get('id'))[0]
                        replyUrl = 'http://dyn.ithome.com//ithome/getajaxdata.aspx?commentid=' + replyid + '&type=getmorelou'
                        self.storeurl(replyUrl, params.originalurl, AllComments.STEP_4)

            elif params.step is AllComments.STEP_4:
                soup = BeautifulSoup(params.content, 'html5lib')
                infos = soup.select('li.gh')
                if infos.__len__() == 0:
                    return
                self.processReply(params, infos)
        except Exception, e:
            traceback.print_exc()
            Logger.getlogging().error(e.message)

    def processReply(self, params, replys):
        for reply in replys[0:]:
            reply_content = reply.select('div.re_comm > p')[0].get_text().strip()
            reply_content = reply_content.decode('utf8').encode('utf8')
            reply_timestr = reply.select('div > span.posandtime')[0].get_text().strip()
            reply_curtime = self.r.parse('(\d+-\d+-\d+ \d+:\d+:\d+)', reply_timestr)[0]
            reply_nick = reply.select('strong.nick')[0].get_text().strip()
            if not reply_nick:
                reply_nick = reply_nick.get('nickname', 'anonymous')
            if not CMTStorage.exist(params.originalurl, reply_content, reply_curtime, reply_nick):
                CMTStorage.storecmt(params.originalurl, reply_content, reply_curtime, reply_nick)


