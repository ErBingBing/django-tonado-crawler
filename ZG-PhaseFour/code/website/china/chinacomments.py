# encoding=utf-8

#################################################################################
# @file: chinacomments.py
# @author：JiangSiwei
# @date：2016/12/1 -> 2017/09/12 modified by Han Luyang
# @note：获取中华网评论的文件
#################################################################################
import re
import urllib
import json
import math
from utility.timeutility import TimeUtility
from utility.common import Common
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from log.spiderlog import Logger
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
from configuration import constant
from bs4 import BeautifulSoup 
#################################################################################
# @class: ChinaComments
# @author：JiangSiwei
# @date：2016/12/1 -> 2017/09/12 modified by Han Luyang
# @note：获取中华网评论的类，继承于SiteComments类
#################################################################################
class ChinaComments(SiteComments):
    STEP_COMMENT_FIRST_PAGE = None
    STEP_COMMENT_EACH_PAGE  = 'each_news'
    STEP_CLUB_NONE = None
    STEP_CLUB_FIRST_PAGE = 'club_first'
    STEP_CLUB_EACH_PAGE = 'club_each'
    
    def __init__(self):
        SiteComments.__init__(self)
        # club评论的分页url模板
        self.club_counturl = 'http://st01.club.china.com/data/thread/{path}_threadpage.js'
        self.club_commonurl = 'http://st01.club.china.com/data/thread/{path}_{page}_re.js'
        # 其他，如：news,sports,lady等评论的分页url模板
        self.new_firsturl = 'http://pl.china.com/CommentInfoAction.do?processID=listNewsComment&order=desc' \
                             '&newsobjectid={objectid}&channelcode={channel}&pageindex={pageno}&typeobjectid={type}' \
                             '&clienttype={clienttype}&key=N_F_P_{key}'
        # 相比第一页评论，之后的评论页url多了一个参数：lastCommentId，指第一页评论的最后一个评论id
        self.new_commonurl = 'http://pl.china.com/CommentInfoAction.do?processID=listNewsComment&order=desc' \
                             '&newsobjectid={objectid}&channelcode={channel}&pageindex={pageno}&typeobjectid={type}' \
                             '&clienttype={clienttype}&key=N_F_P_{key}&lastCommentId={lastcmtid}'
        
        self.club_pagesize = 100.0
        self.news_pagesize = 3.0        

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：None
    # @author：JiangSiwei
    # @date：2016/11/28 -> 2017/09/12 modified by Han Luyang
    # @note：step0：判断原始url是来自CLUB还是OTHERS（包括news，sports，lady等），拼接出可以得到cmtNum
    #               的url，并向共通模块传递；
    #        step1(club|others)：对应club和others，处理得到cmtNum；拼接处（全量/增量）的分页url，并向
    #               共通模块传递；
    #        step2(club|others): 对应club和others，处理分页页面，解析出评论信息
    ##############################################################################################                
    def process(self, params):
        try:
            pattern = 'https?://club\.china\.com/.*'
            if self.r.search(pattern, params.originalurl):
                self.process_club(params)
            else:
                self.process_news(params)
        except:
            Logger.printexception() 

    #----------------------------------------------------------------------
    def process_news(self, params):
        if params.step == self.STEP_COMMENT_FIRST_PAGE:
            self.step1_news(params)
        elif params.step == self.STEP_COMMENT_EACH_PAGE:
            self.step2_news(params)
            
    #----------------------------------------------------------------------
    def process_club(self,params):
        if params.step == self.STEP_CLUB_NONE:
            self.step1_club(params)
        elif params.step == self.STEP_CLUB_FIRST_PAGE:
            self.step2_club(params)
        elif params.step == self.STEP_CLUB_EACH_PAGE:
            self.step3_club(params)

    #----------------------------------------------------------------------
    def step1_news(self, params):
        paramList = None
        if params.content.find('showinputc') >-1:
            paramList = self.r.parse('showinputc\((.*?);', params.content)[0].replace('\'', '').split(',')
        elif params.content.find('showsouhuinputc') >-1:
            paramList = self.r.parse('showsouhuinputc\((.*?);', params.content)[0].replace('\'', '').split(',')
        if not paramList:
            return 
        clienttype = paramList[0]
        channel = paramList[1]
        type = paramList[3]
        objectid = paramList[6]
        key = channel + '_' + objectid    
        comment_url = self.new_firsturl.format(objectid=objectid, channel=channel, type=type, 
                                               clienttype=clienttype, key=key, pageno=0)
        self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_EACH_PAGE,
                                {'objectid':objectid, 'channel':channel, 'type':type, 'clienttype':clienttype, 'key':key, 'pageno':1})
    
    #----------------------------------------------------------------------
    def step2_news(self, params):
        objectid = params.customized['objectid']
        channel = params.customized['channel']
        type = params.customized['type']
        clienttype = params.customized['clienttype']
        key = params.customized['key']
        pageno = params.customized['pageno']
        
        content = params.content
        try:
            data = content[content.index('{'): content.rindex('}')+1]
        except:
            return
            Logger.printexception()
        data = json.loads(data)
        datalist = data['list']
        if not datalist:
            return
        timelist = []
        for item in datalist:
            curtime = item['createTime']
            content = item['content']
            CMTStorage.storecmt(params.originalurl, content, curtime, '')   
            timelist.append(TimeUtility.getuniformtime(curtime))
        curcmtnum = data['cnum']
        if pageno == 1:
            NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        if not self.isnewesttime(params.originalurl, min(timelist)):
            return
        #dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        #pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.news_pagesize))
        pages = int(math.ceil(float(curcmtnum) / self.news_pagesize))
        if pageno >= self.maxpages or pageno >= pages:
            return
        lastcmtid = data['list'][-1]['id']
        pageno = pageno + 1
        comment_url = self.new_commonurl.format(objectid=objectid, channel=channel, type=type, 
                                                clienttype=clienttype, key=key, pageno=pageno, lastcmtid=lastcmtid)
        self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_EACH_PAGE,
                    {'objectid':objectid, 'channel':channel, 'type':type, 'clienttype':clienttype, 'key':key, 'pageno':pageno})
        
    #----------------------------------------------------------------------
    def step1_club(self, params):
        path = re.findall('http://club\.china\.com/data/thread/(.*)_.*',params.originalurl)
        if not path:
            return
        url = self.club_counturl.format(path=path[0])
        self.storeurl(url, params.originalurl, self.STEP_CLUB_FIRST_PAGE, {'path': path[0]})        
    #----------------------------------------------------------------------
    def step2_club(self, params):
        path = params.customized['path']    
        curcmtnum = int(self.r.getid('rewardpoints', params.content, split=':'))
        #self.club_pagesize = self.r.getid('numperpage', params.content, split=':')
        NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        if dbcmtnum >= curcmtnum:
            return    
        # 循环取得评论的url
        pages = int(math.ceil(float(curcmtnum - dbcmtnum) / self.club_pagesize)) 
        if pages >= self.maxpages:
            pages = self.maxpages
        for page in range(1, pages+1):
            url = self.club_commonurl.format(path=path, page=page)
            self.storeurl(url, params.originalurl, self.STEP_CLUB_EACH_PAGE, {'path': path})
    #----------------------------------------------------------------------
    def step3_club(self, params):
        content = params.content
        data = content[content.index('{'): content.rindex('}')+1]
        data = json.loads(data) 
        for item in data['l']:
            try:
                curtime = item['cd']
                pcontent = item['nr']
                comment = XPathUtility(pcontent).getstring('//p')
                CMTStorage.storecmt(params.originalurl, comment, curtime, '')
            except:
                Logger.printexception()
            