# encoding=utf-8
##############################################################################################
# @file：MopComments.py
# @author：
# @date：
# @version：Ver0.0.0.100
# @note：猫扑新闻页获取评论的文件
###############################################################################################
import json
import time
import re
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
##############################################################################################
# @class：MopComments
# @author：
# @date：
# @note：猫扑新闻页获取评论的类，继承于SiteComments类
##############################################################################################
class MopComments(SiteComments):
                        #http://tt3.mop.com/subject/getReplyList?subid=15743784&pageNum=1&type=0
    COMMENTS_URL_TT = 'http://tt3.mop.com/subject/getReplyList?subid={subid}&pageNum={page}&type=0'
    COMMENTS_URL_DZH = 'http://dzh3.mop.com/ajax/reply/getReplayByPage?subjectId={subid}&page={page}&isMaster=false'
    # COMMENTS_URL_DZH = 'http://comment.mop.com/mopcommentapi/dzh/replylist/api/v170828/replyat/offset/asc/{subid}/{limit}/100'
    INFO_URL_TT ='http://staticize.mop.com/subject/getArticleById?id={id}&type=tt'
    INFO_URL_DZH = 'http://staticize.mop.com/subject/getArticleById?id={id}&type=dzh'
    LIMIT = 100
    PAGE_SIZE = 100
    STEP_1 = None
    STEP_2 = 2
    STEP_DZH_2_1 = '2_1'
    STEP_TT_2_1 = '2_1'
    STEP_3 = 3
    SET_CLICKNUM_TT = 4
    SET_CLICKNUM_DZH = 5


    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：猫扑新闻页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent=None):
        SiteComments.__init__(self)
        if parent:
            self.website = parent.website
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @note：Step1：通过共通模块传入的html内容获取到articleId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        if self.r.search('http://dzh\.mop\.com/',params.originalurl):
            self.processdzh(params)
        elif self.r.search('http://tt\.mop\.com/',params.originalurl):
            self.processtt(params)

    
    
    def processdzh(self, params):
        try:
            if params.step is MopComments.STEP_1:
                self.step1dzh(params)
            elif params.step == MopComments.STEP_2:
                self.step2dzh(params)
            elif params.step == MopComments.STEP_DZH_2_1:
                self.step2_1dzh(params)
            elif params.step == MopComments.STEP_3:
                self.step3dzh(params)
            elif params.step == MopComments.SET_CLICKNUM_DZH:
                self.getinfo(params)

        except Exception,e:
            Logger.printexception()
    ##############################################################################################
    # @functions：step1dzh
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1dzh(self, params):
        pattern = '<input id="articleid" type="hidden" value="(\d+)">'
        if self.r.search(pattern, params.content):
            subid = self.r.parse(pattern, params.content)[0]
            commenturl = MopComments.COMMENTS_URL_DZH.format(subid=subid, page=1)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_2, {'subid':subid})
            # commenturl = MopComments.COMMENTS_URL_DZH.format(subid=subid, limit = 0)
            # self.storeurl(commenturl, params.originalurl, MopComments.STEP_2, {'subid': subid})
            # 通过xpath获取的clicknum有误，需要js请求获取
            clickulr = MopComments.INFO_URL_DZH.format(id=subid)
            self.storeurl(clickulr, params.originalurl, MopComments.SET_CLICKNUM_DZH)
        else:
            Logger.getlogging().debug('{url} can\'t find subid'.format(url=params.originalurl))
            return
    ##############################################################################################
    # @functions：step2dzh
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2dzh(self, params):
        try:
            subid = params.customized['subid']
            jsondata = json.loads(params.content)
            comments_count = jsondata['page']['pageInfo']['totalCounts']
            NewsStorage.setcmtnum(params.originalurl, comments_count)
            pagenum = int(jsondata['page']['pageInfo']['allPage'])
            cmtnum = CMTStorage.getcount(params.originalurl, True)
            if cmtnum >= comments_count:
                return
            if pagenum >= self.maxpages:
                pagenum = self.maxpages

        ##############################################
            start = int(cmtnum /self.PAGE_SIZE) + 1
            end = int(pagenum)
            if end > start + self.maxpages:
                start = end - self.maxpages

            params.customized['page'] = 1
            if end == 1:
                self.step3dzh(params)
                return
            if start == 1:
                self.step3dzh(params)
            commenturl = MopComments.COMMENTS_URL_DZH.format(subid=subid, page=end)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_DZH_2_1,{'subid':subid, 'page':end,
	                                                                    'start':start, 'end':end})
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))
    def step2_1dzh(self, params):
        #获取最后一页
        start = params.customized['start']
        end = params.customized['end']
        subid = params.customized['subid']
        for page in range(end, start - 1, -1):
            if int(page) == end:
                if not self.step3dzh(params):
                    break
                continue
            if int(page) == 1:
                continue
            commenturl = MopComments.COMMENTS_URL_DZH.format(subid=subid, page=page)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_3)
    ##############################################################################################
    # @functions：step3dzh
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3dzh(self, params):
        try:
            jsondata = json.loads(params.content)
            if jsondata:
                publishlist = [TimeUtility.getcurrentdate(TimeUtility.DEFAULTFORMAT)]
                try:
                    if  jsondata == "ERROR_PARAMETER":
                        return
                    entitylist = jsondata['page'].get('entityList',[])
                    for comment in entitylist:
                        content = self.strfilter(comment['content'])
                        #Jul 3, 2017 4:46:30 PM
                        curtime = comment['date']
                        #此处时间格式
                        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(curtime, '%b %d, %Y %H:%M:%S %p'))
                        nick = comment['un']
                        publishlist.append(curtime)
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                except:
                    Logger.printexception()
                    Logger.getlogging().error('extract no comment  from {site}'.format(site=params.url))
                if not self.isnewesttime(params.originalurl, min(publishlist)):
                    return False
                return True
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))          
   
   
    def processtt(self, params):
        try:
            if params.step is MopComments.STEP_1:
                self.step1tt(params)
            elif params.step == MopComments.STEP_2:
                self.step2tt(params)
            elif params.step == MopComments.STEP_TT_2_1:
                self.step2_1tt(params)
            elif params.step == MopComments.STEP_3:
                self.step3tt(params)
            elif params.step == MopComments.SET_CLICKNUM_TT:
                self.getinfo(params)
        except Exception,e:
            Logger.printexception()
    ##############################################################################################
    # @functions：step1tt
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1tt(self, params):
        pattern = '<input id="articleid" type="hidden" value="(\d+)">'
        if self.r.search(pattern, params.content):
            subid = self.r.parse(pattern, params.content)[0]
            commenturl = MopComments.COMMENTS_URL_TT.format(subid=subid, page=1)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_2, {'subid':subid})
            clickulr = MopComments.INFO_URL_TT.format(id = subid)
            self.storeurl(clickulr, params.originalurl, MopComments.SET_CLICKNUM_TT)
        else:
            Logger.getlogging().debug('{url} can\'t find subid'.format(url=params.originalurl))
            return
    ##############################################################################################
    # @functions：step2tt
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2tt(self, params):
        try:
            subid = params.customized['subid']
            jsondata = json.loads(params.content)
            comments_count = jsondata['resultDO']['pageInfo']['totalCounts']
            NewsStorage.setcmtnum(params.originalurl, comments_count)
            pagenum = int(jsondata['resultDO']['pageInfo']['allPage'])
            cmtnum = CMTStorage.getcount(params.originalurl, True)
            if cmtnum >= comments_count:
                return
            if pagenum >= self.maxpages:
                pagenum = self.maxpages
            ##############################################
            start = int(cmtnum / self.PAGE_SIZE) + 1
            end = int(pagenum)
            if end > start + self.maxpages:
                start = end - self.maxpages

            # params.customized['page'] = 1
            if end == 1:
                self.step3tt(params)
                return
            if start == 1:
                self.step3tt(params)
            commenturl = MopComments.COMMENTS_URL_DZH.format(subid=subid, page=end)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_TT_2_1, {'subid': subid, 'page': end,
                                                                                     'start': start, 'end': end})
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))
    def step2_1tt(self, params):
        #获取最后一页
        start = params.customized['start']
        end = params.customized['end']
        subid = params.customized['subid']
        for page in range(end, start - 1, -1):
            if int(page) == end:
                if not self.step3tt(params):
                    break
                continue
            if int(page) == 1:
                continue
            commenturl = MopComments.COMMENTS_URL_TT.format(subid=subid, page=page)
            self.storeurl(commenturl, params.originalurl, MopComments.STEP_3)
    ##############################################################################################
    # @functions：step3tt
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3tt(self, params):
        try:
            jsondata = json.loads(params.content)
            if jsondata:
                publishlist = [TimeUtility.getcurrentdate(TimeUtility.DEFAULTFORMAT)]
                try:
                    if  jsondata == "ERROR_PARAMETER":
                        return
                    entitylist = jsondata['resultDO'].get('entityList',[])
                    for comment in entitylist:
                        content = self.strfilter(comment['body'])
                        #Jul 3, 2017 4:46:30 PM
                        curtime = comment['replyTime']
                        #此处时间格式
                        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(curtime, '%b %d, %Y %H:%M:%S %p'))
                        nick = comment['userName']
                        publishlist.append(curtime)
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                except:
                    Logger.printexception()
                    Logger.getlogging().error('extract no comment  from {site}'.format(site=params.url))
                if not self.isnewesttime(params.originalurl, min(publishlist)):
                    return False
                return True

        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))
    def getinfo(self,params):
        try:
            jsondata = json.loads(params.content)
            clicknum = jsondata['article']['readnum']
            votenum = jsondata['article']['praisenum']
            fansnum = jsondata['article']['favoritenum']
            publishtime = TimeUtility.getuniformtime(jsondata['article']['publishtime'])
            title = jsondata['article']['title']
            data = {}
            data = {"title" : title,"clicknum":clicknum,"votenum":votenum,"fansnum":fansnum,"publishdate":publishtime}
            NewsStorage.seturlinfo(params.originalurl,'','',data)
        except:
            Logger.printexception()

   