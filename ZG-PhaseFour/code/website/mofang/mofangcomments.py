# encoding=utf-8
##############################################################################################
# @file：mofangcomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/21
# @note：土豆整站评论获取

##############################################################################################

import json
import math
import re

from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
from  utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from bs4 import BeautifulSoup


##############################################################################################
# @class：MofangComments
# @author：Merlin.W.OUYANG
# @date：2016/11/21
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class MofangComments(SiteComments):
    COMMENTS_URL = 'http://comment.mofang.com/comment/list?flag=cms:%s&pid=0&pagesize=%s'
    COMMENTS_URL_BBS = 'http://bbs.mofang.com/thread/%s/%d/1.html'
    TID_FORMAT_LIST = ['thread/(\d+).html', 'thread/(\d+)/\d+/\d+.html', 'tid=(\d+).*']
    COUNT_FORMAT_LIST = ['<s class="icon-ask"></s>(\d+)</a></span>', '<span class="xi1">\s*(\d+)\s*</span>']
    PAGE_SIZE = 10 # 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/20
    # @note：AllComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：None
    # @author：Merlin.W.ouyang
    # @date：2016/11/18
    # @note：根据url，判断是视频网页还是论坛网页
    #该网站只保存4条记录，超过4条就截断了，只显示最新的4条
    ##############################################################################################
    def process(self,params):
        # 视频S1
        if self.r.match(r'^http://v\.mofang\.com/.*', params.originalurl):
            self.processVideo(params)
        #论坛S1
        else:
            self.processBBS(params)

    ##############################################################################################
    # @functions：processVideo
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Merlin.W.ouyang
    # @date：2016/11/18
    # @note：Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
    #        Step3：获取增量评论，根据当前页面的第一个时间判断和是否是空白内容判断是否开始获取时间以下分成2种情况处理
    #               case1:增量内容只有一页的时候，程序会根据时间获取增量时间段的评论，然后提交写入后台
    #               case2:增量超过一页的情况，整页部分完全处理，不满足一页按照时间判断增量获取，然后提交写入后台
    #                     当增量数量正好是整页的情况时，根据当前页的第一个时间不满足增量时间段时，程序直接退出
    # 该网站只保存4条记录，超过4条就截断了，只显示最新的4条
    ##############################################################################################
    def processVideo(self, params):
        try:
            if params.step is MofangComments.STEP_1:
                if not self.r.search('data-flag=\"(.*?)\">',params.content):
                    return
                cmsid = self.r.parse('data-flag=\"(.*?)\">',params.content)[0]
                comments_url = MofangComments.COMMENTS_URL % (cmsid,'4')
                self.storeurl(comments_url, params.originalurl, MofangComments.STEP_2, {'cmsid':cmsid,'pagesize':'4'})
            elif params.step is MofangComments.STEP_2:
                comments = json.loads(params.content)
                pagesize=comments['data']['total']
                comments_url = MofangComments.COMMENTS_URL % (params.customized['cmsid'], pagesize)
                self.storeurl(comments_url, params.originalurl, MofangComments.STEP_3,
                                  {'cmsid':params.customized['cmsid'],
                                   'pagesize':pagesize})
            elif params.step is MofangComments.STEP_3:
                comments = json.loads(params.content)
                if params.customized['pagesize'] <> '0':
                    pcontent=[]
                    ptime=[]
                    for key in range(0,int(params.customized['pagesize'])):
                        ptime.append(TimeUtility.getuniformtime2(comments['data']['list'][key]['create_time']))
                        pcontent.append(comments['data']['list'][key]['html_content'])
                    if ptime <> []:
                        index = 0
                        comments=[]
                        complete=False
                        for comment in pcontent:
                            cmti = CommentInfo()
                            cmti.content = comment
                            #只判断时间段为新增时间段的情况下，才写入增量list中
                            if URLStorage.storeupdatetime(params.originalurl, str(ptime[index])):
                                comments.append(cmti)
                                index += 1
                            else:
                                #更新数据库时间
                                complete=True
                                break;                        
                        self.commentstorage.store(params.originalurl, comments)
        except Exception ,e:
            Logger.printexception()


    ##############################################################################################
    # @functions：processBBS
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/12/1
    # @note：Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：根据数据库中的记录的最后一次获取的评论的最新时间，判断是否需要获取该页面的评论数据，并传入中间参数，不需要获取直接退出，需要获取进入step3
    #        Step3：获取增量评论
    ##############################################################################################
    def processBBS(self, params):
        try:
            if params.step is MofangComments.STEP_1:
                # 获取参数id
                id = self.gettidfromurl(params.originalurl) #self.r.parse('thread/(\d+).html', params.originalurl)[0]
                if id is None:
                    Logger.getlogging().error('Unable to get tid')
                    return

                # 获取首页url
                comments_url = MofangComments.COMMENTS_URL_BBS % (id, 1)
                self.storeurl(comments_url, params.originalurl, MofangComments.STEP_2, {'id': id, 'curpage' : 1})


            elif params.step is MofangComments.STEP_2:
                # 获取页数
                comments_count_str = self.getcommentcount(params.content) # self.r.parse('<s class="icon-ask"></s>(\d+)</a></span>', params.content)[0]
                if comments_count_str is None:
                    Logger.getlogging().error('Unable to get comments_count')
                    return
                comments_count = int(comments_count_str)
                if comments_count == 0:
                    return

                # 判断增量
                cmtnum = URLStorage.getcmtnum(params.originalurl)
                if cmtnum >= comments_count:
                    return
                URLStorage.setcmtnum(params.originalurl, comments_count)

                # 获取首页的所有评论
                self.geturlcomments(params, 1)

                # 获取id
                id = params.customized['id']
                # 获取首页之外的所有url(从第二条开始获取）
                for page in range(2, int(math.ceil(float(comments_count) / MofangComments.PAGE_SIZE)) + 1, 1):
                    comments_url = MofangComments.COMMENTS_URL_BBS % (id, page)
                    self.storeurl(comments_url, params.originalurl, MofangComments.STEP_3, {'id': id})

            elif params.step is MofangComments.STEP_3:
                self.geturlcomments(params, 0)

        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：gettidfromurl
    # @url： 寻找tid的目标url
    # @return：tid
    # @author：hedian COUNT_FORMAT_LIST
    # @date：2016/12/16
    # @note：从输入参数的url里获取到tid
    ##############################################################################################
    def gettidfromurl(self, url):
        tid = None
        for fm in self.TID_FORMAT_LIST:
            if self.r.search(fm, url):
                tid = self.r.parse(fm, url)[0]
                break
        return tid

    ##############################################################################################
    # @functions：getcommentcount
    # @html： 下载平台返回的html内容
    # @return：评论数
    # @author：hedian
    # @date：2016/12/16
    # @note：从输入参数html的里获取到评论数
    ##############################################################################################
    def getcommentcount(self, html):
        count = None
        for fm in self.COUNT_FORMAT_LIST:
            if self.r.search(fm, html):
                count = self.r.parse(fm, html)[-1] #最后一个是回复数，第一个是查看数
                break
        return count

    ##############################################################################################
    # @functions：geturlcomments
    # @params： 共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @startpos: 获取评论的开始为止（从那条评论开始获取，0：表示默认为第一条）
    # @return：none
    # @author：hedian
    # @date：2016/12/16
    # @note：从输入参数里获取到该页的评论（首页第一条当作是正文）
    ##############################################################################################
    def geturlcomments(self, params, startpos = 0):
        # 取得所有评论
        soup = BeautifulSoup(params.content, 'html5lib')
        comments = soup.select('.info')
        commentTimes = soup.select('.date')
        commentsInfo = []

        # //*[contains(@id,"postmessage_")]
        if len(comments) <= 0:
            tds = soup.select('td.plc') # soup.find_all("td", attrs={"class": "plc"})
            if tds is None:
                return
            for td in tds:
                timestr = td.find(attrs={'id': re.compile('authorposton')})
                if not timestr:
                    continue
                commentTimes = getuniformtime(timestr.get_text())
                if URLStorage.storeupdatetime(params.originalurl, commentTimes):
                    contents = td.find(attrs={'id': re.compile('postmessage_')})
                    if contents:
                        cmti = CommentInfo()
                        cmti.content = contents.get_text()
                        commentsInfo.append(cmti)

        else:
            # 取得所有评论
            for index in range(startpos, int(len(comments)), 1):
                # 提取时间
                cmti = CommentInfo()
                publicTime = getuniformtime(commentTimes[index].get_text()).strip()
                #publicTime = self.r.parse(ur'发表于(.*)', publicTime)[0].strip()
                tm = TimeUtility.getuniformtime(TimeUtility.getuniformtime(publicTime, u'%Y-%m-%d %H:%M'))
                if URLStorage.storeupdatetime(params.originalurl, tm):
                    cmti.content = comments[index].get_text()
                    commentsInfo.append(cmti)

        if len(commentsInfo) > 0:
            self.commentstorage.store(params.originalurl, commentsInfo)