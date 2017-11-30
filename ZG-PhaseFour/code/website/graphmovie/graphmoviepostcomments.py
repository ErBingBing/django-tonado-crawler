# encoding=utf8

##############################################################################################
# @file：graphmovieComments.py
# @author：Jiangsiwei
# @date：
# @version：
# @note：图解电影获取评论的文件
##############################################################################################
import json
import traceback
from website.common.comments import SiteComments
from utility.common import Common 
from log.spiderlog import Logger
from storage.commentsstorage import CommentInfo
from storage.urlsstorage import URLStorage
from utility.timeutility import TimeUtility
from utility.gettimeutil import getuniformtime
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup 
import re

##############################################################################################
# @class：GraphmovieComments
# @author：Liuyonglin
# @date：2016/12/16
# @version：Ver0.0.0.100
# @note：图解电影获取评论的文件
##############################################################################################
class GraphmoviePostComments(SiteComments):
   
    commen_url_1 = 'http://www.graphmovies.com/home/2/get.php?orkey={orkey}'
    commen_url_2 = 'http://h5.graphmovie.com/appweb/news/comment.2.php?paperid={paperid}'
    post_url = ''
    post_data = {}
    STEP_1 = None
    STEP_2 = '2'
    STEP_2_2 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liuyonglin
    # @date：2016/12/16
    # @note：GraphmovieComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self,parent=None):
        SiteComments.__init__(self)
        self.page_size = 10
        self.orkey_patttern = '\'get.php\?orkey=(.*)\''
        if parent:
            self.website = parent.website
        
    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == self.STEP_1:
            #1、图解电影 2、电影课堂
            if self.r.search('http[s]{0,1}://h5\.graphmovie\.com/appweb/news/share_(\d+).html',params.originalurl):
                self.step1_2(params)
            else:
                self.step1(params)
        elif params.step == self.STEP_2:
            self.step2(params)
        elif params.step == self.STEP_2_2:
            self.step2_2(params)
            
    #图解电影    
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        if not self.r.search(self.orkey_patttern,params.content):
            return
        orkey = self.r.parse(self.orkey_patttern,params.content)[0]
        self.post_url = Common.urldec(self.commen_url_1.format(orkey=orkey))
        self.post_data['type'] = 'm_comments'
        self.post_data['p'] = '0'
        self.post_data['t'] = '0'
        self.storeposturl(self.post_url, params.originalurl, self.STEP_2, self.post_data)
    
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        print params.content
        try:
            jsondata = json.loads(params.content)
            comments_total = int(jsondata['comments_total'])
            comments_data = jsondata['comments'] 
        except:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))            
            return   
        #cmtnum = URLStorage.getcmtnum(params.originalurl)
        #if cmtnum >= comments_total:
            #return
        #URLStorage.setcmtnum(params.originalurl, comments_total)  
        
        comments = []
        for comment in comments_data:
            cmti = CommentInfo()
            cmti.content = comment['txtcontent']
            tm = comment['addtime']
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)
        if len(comments) > 0:
            # 保存获取的评论
            self.commentstorage.store(params.originalurl, comments)    
        
        self.post_data['p'] = str(int(self.data['p']+self.page_size))
        self.post_data['t'] = TimeUtility.getuniformdate(tm, '%Y-%m-%d+%H%M%S')
        self.storeposturl(self.post_url, params.originalurl, self.STEP_2, self.post_data)
        
    #电影课堂
    #http://h5.graphmovie.com/appweb/news/share_1482.html   
    #----------------------------------------------------------------------
    def step1_2(self,params):
        """"""
        if not self.r.search('http[s]{0,1}://h5\.graphmovie\.com/appweb/news/share_(\d+).html',params.originalurl):
            return 
        paperid = self.r.parse('http[s]{0,1}://h5\.graphmovie\.com/appweb/news/share_(\d+).html',params.originalurl)[0]
        url = GraphmoviePostComments.commen_url_2.format(paperid=paperid)
        data = {}
        #self.storeurl(url, params.originalurl, self.STEP_2_2)
        self.storeposturl(url, params.originalurl, self.STEP_2_2, data)
    
    #----------------------------------------------------------------------
    def step2_2(self,params):
        """"""
        try:
            jsondata = json.loads(params.content)
            data = jsondata['data']
            soup = BeautifulSoup(data,'html5lib')
            divs = soup.select('.comment')
        except:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))            
            return
        #comments_total = len(divs)
        #cmtnum = URLStorage.getcmtnum(params.originalurl)
        #if cmtnum >= comments_total:
            #return
        #URLStorage.setcmtnum(params.originalurl, comments_total)           
        comments = []
        #divs.reverse()
        for div in divs:
            cmti = CommentInfo()
            cmti.content = div.find(attrs={'style':re.compile('padding-top')}).get_text().strip()
            tm = div.select_one('.show-time').get_text()
            tm = getuniformtime(tm)
            if not tm:
                continue
            if URLStorage.storeupdatetime(params.originalurl, tm):
                comments.append(cmti)
        if len(comments) > 0:
            # 保存获取的评论
            self.commentstorage.store(params.originalurl, comments)
            
    ###----------------------------------------------------------------------
    #def step2_3(self,params):
        #""""""
        #jsondata = json.loads(params.content)
        #datas = jsondata['dm']
        
        #comments_total = len(datas)
        #cmtnum = URLStorage.getcmtnum(params.originalurl)
        #if cmtnum >= comments_total:
            #return
        #URLStorage.setcmtnum(params.originalurl, comments_total)         
        #comments = []
        #for data in datas:
            #cmti = CommentInfo()
            #cmti.content = data['comment']
            #comments.append(cmti)
        #if len(comments) > 0:
            ## 保存获取的评论
            #self.commentstorage.store(params.originalurl, comments)            
         
        
            
        
        
        
    
        


    
    
                
                
                
                
                
            
            
                
        
        