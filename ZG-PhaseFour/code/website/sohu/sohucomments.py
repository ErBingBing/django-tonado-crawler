# coding=utf8

#################################################################################
# @class：SohuComments
# @author：JiangSiwei
# @date：2017/06/28
# @note：搜狐获取评论的文件，继承于WebSite类
#################################################################################

import json
import math
import re
from configuration import constant
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from website.common.comments import SiteComments
from website.common.changyanComments import ChangyanComments
from storage.newsstorage import NewsStorage

class SohuComments(SiteComments):
    def __init__(self,parent = None):
        SiteComments.__init__(self)
        self.page_size = 20
        self.tv_page_size = 30
        self.client_id = 'cyqemw6s1' 
        self.tv_client_id = 'cyqyBluaj'
        self.group_mark = '9000' 
        if parent:
            self.website = parent.website
        
        self.COMMENTS_SOURCE_URL = 'http://changyan.sohu.com/api/3/topic/liteload?client_id={0}&topic_source_id={1}&page_size={2}'
        self.TV_COMMENTS_SOURCE_URL = 'http://changyan.sohu.com/api/2/topic/load?client_id={0}&topic_url={1}&topic_source_id={2}&page_size={3}'
        self.COMMENTS_URL = 'http://changyan.sohu.com/api/2/topic/comments?client_id={0}&topic_id={1}&page_no={2}&page_size={3}'
        self.NEW_NEWS_COMMONURL = 'http://apiv2.sohu.com/api/topic/load?page_size={page_size}&topic_source_id={cmt_id}&page_no={page}&media_id={media_id}&topic_category_id={topic_category_id}'
        self.NEW_NEWS_COMMONURL2 = 'http://apiv2.sohu.com/api/comment/list?page_size={page_size}&topic_id={topic_id}&page_no={page}'
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_NEXT_PAGE = 2     
        self.STEP_TVCLICK = 'tvclick'
        self.STEP_MYTVCLICK = 'mytvclick'
        
        self.STEP_NEWS_A2 = 'step2_new_a'
        self.STEP_NEWS_A3 = 'step3_new_a'
        self.TVCLICKURL = 'http://count.vrs.sohu.com/count/queryext.action?vids={vid}'
        self.MYTVCLICKURL = 'http://vstat.my.tv.sohu.com/dostat.do?method=getVideoPlayCount&v={vid}'
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：JiangSiwei
    # @date：2016/11/17
    # @note：Step1：通过共通模块传入的html内容获取到topic_source_id，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数及topic_id，拼出获取评论的url，并传递给共通模块
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则保存最新更新时间
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则抓取新增的数据
    ##############################################################################################        
    #----------------------------------------------------------------------          
    def process(self, params):
        """"""
        #过滤掉不在范围内的网站或url
        patterns = ['^http[s]{0,1}://(news|fashion|women|mil|health|cul|travel|history|learning|book|star.news|sports|(music\.)?yule|baobao|chihe|it|business|mgame)\.sohu\.com/.*',
                    '^http[s]{0,1}://pic\.\w+\.sohu\.com/.*',
                    '^http[s]{0,1}://gongyi\.sohu\.com/.*',
                    '^http[s]{0,1}://pic\.book\.sohu\.com/.*',
                    '^http[s]{0,1}://tv\.sohu\.com/.*',
                    '^http[s]{0,1}://my\.tv\.sohu\.com/.*',
                    '^http[s]{0,1}://www\.sohu\.com.*',
                    '^http[s]{0,1}://p\.weather\.com\.cn.*'
                    ]

        flag = False
        for pattern in patterns:
            if self.r.search(pattern,params.originalurl):
                flag = True
                break
        if not flag:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
            return
        if self.r.search('https?://www\.sohu\.com/a/\d+_\d+', params.originalurl):
            self.process_new_a(params)
        elif self.r.search('^http[s]{0,1}://(www|news)\.sohu\.com.*|^http[s]{0,1}://p\.weather\.com\.cn.*',params.originalurl):
            ChangyanComments(self).process(params)
        else:
            self.process_video(params)
        
        
    #----------------------------------------------------------------------
    def process_video(self, params):
        try:
            if params.step == None:
                self.step1(params)
            elif params.step == self.STEP_COMMENT_FIRST_PAGE:
                self.step2(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step3(params)    
            elif params.step == self.STEP_MYTVCLICK:
                self.setclicknum_mytv(params)  
            elif params.step == self.STEP_TVCLICK:
                self.setclicknum_tv(params) 
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1(self,params):
        """获取评论的首页url""" 
        try:
            comment_source_url = ''
            if self.r.search('http[s]{0,1}://.*tv\.sohu\.com.*',params.originalurl):
                #对于电影,电视剧,搜狐手游取topic_source_id页面字段来源不同
                if self.r.search('^http://tv\.sohu\.com/\d{8}/n\d+\.shtml',params.originalurl):
                    topic_source_id = self.r.parse('var[\s]*vid[\s]*=[\s]*\"(.+?)\"',params.content)
                    if topic_source_id:
                        topic_source_id = topic_source_id[0]
                    else:
                        Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
                        return
                elif self.r.search('^http://my\.tv\.sohu\.com/.*.shtml',params.originalurl):
                    topic_source_id = self.r.parse('\d{1,}',params.originalurl)[-1]
                    topic_source_id = 'bk'+topic_source_id
                else:
                    topic_source_id = self.r.getid('PLAYLIST_ID', params.content)
                    if not topic_source_id:
                        topic_source_id = self.r.getid('playlistId', params.content)
                    if not topic_source_id:
                        Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
                        return                      
                    topic_source_id = 'vp'+topic_source_id
                comment_source_url = self.TV_COMMENTS_SOURCE_URL.format(self.tv_client_id,params.originalurl,topic_source_id,self.tv_page_size)

            else:
                if self.r.parse('group',params.originalurl):
                    topic_source_id = \
                    self.r.parse('http[s]{0,1}://.*\.sohu\.com/group-(\d+)\.shtml.*', params.originalurl)[0]
                    comment_source_url = self.COMMENTS_SOURCE_URL.format(self.client_id,self.group_mark+topic_source_id,self.page_size)    
                else:
                    topic_source_id = \
                    self.r.parse('http[s]{0,1}://.*\.sohu\.com/\d{8}/n(\d+)\.shtml.*', params.originalurl)[0]
                    comment_source_url = self.COMMENTS_SOURCE_URL.format(self.client_id,topic_source_id,self.page_size)
         
            self.storeurl(comment_source_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE) 
            #http://tv.sohu.com/20170831/n600133376.shtml
            #http://tv.sohu.com/s2015/newslist/?vid=4016103  暂无法取得
            #对播放量进行检查，如果xpath没有获取到，使用代码通过api获取
            if NewsStorage.getclicknum(params.originalurl) <= 0:
                if re.search('^http://tv\.sohu\.com/\d{8}/n\d+\.shtml',params.originalurl):
                    vid = self.r.getid('vid',params.content, split='=')
                    clickurl = self.TVCLICKURL.format(vid=vid)
                    self.storeurl(clickurl, params.originalurl, self.STEP_TVCLICK)  
                elif re.search('^http://tv\.sohu\.com/.*vid=(\d+)',params.originalurl):
                    vid = self.r.parse('^http://tv\.sohu\.com/.*vid=(\d+)',params.originalurl)[0]
                    clickurl = self.TVCLICKURL.format(vid=vid)
                    self.storeurl(clickurl, params.originalurl, self.STEP_TVCLICK)                 
                elif re.search('^http[s]{0,1}://my\.tv\.sohu\.com.*\.shtml$',params.originalurl):
                    clickurl = self.MYTVCLICKURL.format(vid=params.originalurl.split('/')[-1].split('.')[0])
                    self.storeurl(clickurl, params.originalurl, self.STEP_MYTVCLICK) 
            if re.search('^http[s]{0,1}://my\.tv\.sohu\.com.*\.shtml$',params.originalurl):
                if not params.content:
                    Logger.getlogging().debug("no params.content")
                if not self.r.search('uploadTime: \'(.*)?\'', params.content) :
                    Logger.getlogging().debug("no params.content uploadTime")
                if self.r.search('uploadTime: \'(.*)?\'',params.content):
                    publishdate = self.r.parse('uploadTime: \'(.*)?\'',params.content)[0]
                    NewsStorage.setpublishdate(params.originalurl, TimeUtility.getuniformtime(publishdate))                    
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.url))  

    #----------------------------------------------------------------------
    def  step2(self,params):
        """获取评论的其他url"""
        try:
            comments = json.loads(params.content)
            topic_id = comments['topic_id']
            curcmtnum = float(comments.get('cmt_sum',-1))
            #clicknum = float(comments.get('participation_sum',-1))
            NewsStorage.setcmtnum(params.originalurl, curcmtnum)
            #NewsStorage.setclicknum(params.originalurl, clicknum) 
            
            dbcmtnum = CMTStorage.getcount(params.originalurl, True)
            if dbcmtnum >= curcmtnum:
                return
            page_num=int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
            if page_num >= self.maxpages:
                page_num = self.maxpages
            for page in range(1,page_num+1):
                if self.r.search('http[s]{0,1}://.*tv\.sohu.com/.*',params.originalurl):
                    url=self.COMMENTS_URL.format(self.tv_client_id,topic_id,page,self.tv_page_size)
                else:
                    url=self.COMMENTS_URL.format(self.client_id,topic_id,page,self.page_size)
                self.storeurl(url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE)
        except: 
            Logger.printexception()
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
        
    #----------------------------------------------------------------------
    def  step3(self,params):
        """通过评论的url获取评论"""
        #相对之前的版本，本次更新变动：
        #comments存储的接口为CMTStorage.storecmt(),参数为originalurl, 评论内容, 评论发布时间, 用户
        #存储的内容增加了 评论发布时间, 用户
        try:
            jsondata = json.loads(params.content)
            if jsondata['comments']:
                for comment in jsondata['comments']:
                    content = comment['content']
                    curtime = TimeUtility.getuniformtime(comment['create_time'])
                    nick = comment['passport']['nickname']
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)     
                    reply = comment['comments']
                    while reply:
                        for comment in comment['comments']:
                            content = comment['content']
                            curtime = TimeUtility.getuniformtime(comment['create_time'])
                            nick = comment['passport'].get('nickname','anonymous')
                            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                                CMTStorage.storecmt(params.originalurl, content, curtime, nick)                               
                            reply = comment['comments']
        except:
            Logger.printexception()
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
    
    #----------------------------------------------------------------------
    def setclicknum_mytv(self, params):
        todayplaynum = self.r.getid("count", params.content)
        NewsStorage.setclicknum(params.originalurl, todayplaynum)    
    #----------------------------------------------------------------------
    def setclicknum_tv(self, params):
        todayplaynum = self.r.getid("total", params.content, split=':')
        NewsStorage.setclicknum(params.originalurl, todayplaynum)  
        
        
    #----------------------------------------------------------------------
    def process_new_a(self, params):
        try:
            if params.step == None:
                self.step1_news_a(params)
            elif params.step == self.STEP_NEWS_A2:
                self.step2_news_a(params)            
            elif params.step == self.STEP_NEWS_A3:
                self.step3_news_a(params) 
        except:
            Logger.printexception()
    #----------------------------------------------------------------------
    def step1_news_a(self, params):
        media_id= self.r.getid('media_id', params.content, split=':')
        topic_category_id = self.r.getid('channel_id', params.content, split=':')
        cmt_id = self.r.getid('cms_id', params.content, split=':')
        if int(cmt_id) == 0 and int(topic_category_id) == 19 :
            cmt_id = 'mp_' + self.r.getid('news_id', params.content, split=':')
        url = self.NEW_NEWS_COMMONURL.format(page_size=self.page_size, cmt_id=cmt_id, page=1,
                                             media_id=media_id, topic_category_id=topic_category_id)
        self.storeurl(url, params.originalurl, self.STEP_NEWS_A2, 
                      {'cmt_id':cmt_id, 'topic_category_id':topic_category_id, 'media_id':media_id, 'cms_id':cmt_id})  
    
    #----------------------------------------------------------------------
    def step2_news_a(self, params):
        jsondata = json.loads(params.content)
        topic_id = jsondata['jsonObject']['topic_id']
        curcmtnum = jsondata['jsonObject']['cmt_sum']
        NewsStorage.setcmtnum(params.originalurl, curcmtnum)
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        if dbcmtnum >= curcmtnum:
            return
        page_num=int(math.ceil(float(curcmtnum - dbcmtnum) / self.page_size))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        for page in range(1,page_num+1):
            if page == 1:
                self.step3_news_a(params)
                continue
            url = self.NEW_NEWS_COMMONURL2.format(page_size=self.page_size, page=page, topic_id=topic_id)
            self.storeurl(url, params.originalurl, self.STEP_NEWS_A3)

    #----------------------------------------------------------------------
    def step3_news_a(self, params):
        jsondata = json.loads(params.content)
        comments = jsondata['jsonObject']['comments']
        for comment in comments:
            try:
                content = comment['content']
                curtime = comment['create_time']
                CMTStorage.storecmt(params.originalurl, content, curtime, '')  
            except:
                Logger.printexception()
            
        
    
   
        
        

            
        
    
    
    
    