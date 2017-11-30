# coding=utf-8

##############################################################################################
# @file：laohtposrComments.py
# @author：Jiangsiwei
# @date：2017/03/08
# @version：
# @note：老虎游戏news获取评论的文件
##############################################################r################################

import json
import datetime
import traceback
import math
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime
from utility.xpathutil import XPathUtility
from bs4 import  BeautifulSoup
import re
##############################################################################################
# @class：laohuComments
# @author：HuBorui
# @date：2016/11/29
# @note：老虎游戏论坛获取评论的类，继承于SiteComments类
##############################################################################################
class LaohuPostComments(SiteComments):
    post_url = 'http://member.laohu.com/comment/ajax'
    post_data = {'page':'','token':'','order':'default'}
    comment_url = 'http://member.laohu.com/comment/show/?token={token}'
    STEP1 = None
    STEP2 = 'step2'
    STEP3 = 'step3'
    STEP4 = 'step4'
    page_size = 15
    
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：
    # @date：
    # @note：huxiuComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self,parent=None):
        SiteComments.__init__(self)
        self.r = RegexUtility()
        if parent:
            self.website = parent.website 
            
    #----------------------------------------------------------------------        
    def process(self, params):
        try:
            if params.step is None:
                self.step1(params)
            elif params.step == LaohuPostComments.STEP2:
                self.step2(params)
            elif params.step == LaohuPostComments.STEP3:
                self.step3(params)
        except:
            Logger.printexception()        
    #----------------------------------------------------------------------
    def step1(self,params):
        """"""
        soup = BeautifulSoup(params.content,'html5lib')
        if not soup.select_one('#t_token'):
            Logger.getlogging().debug('{}:30000 no comments'.format(params.originalurl))
            return          
        t_token = soup.select_one('#t_token').get_text()
        url = LaohuPostComments.comment_url.format(token=t_token)
        self.storeurl(url, params.originalurl, self.STEP2)
        
    #----------------------------------------------------------------------
    def step2(self,params):
        """"""
        soup = BeautifulSoup(params.content,'html5lib')
        if not soup.select_one('.filter-by-type'):
            Logger.getlogging().debug('{}:30000 no comments'.format(params.originalurl))
            return        
        token =  self.r.getid('source_id',params.content)
        LaohuPostComments.post_data['token'] = token
        
        comment_num = soup.select_one('.filter-by-type').get_text()
        comment_num = re.findall('(\d+)',comment_num)[0]
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comment_num:
            #Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return        
        page_num = int(math.ceil(float(comment_num)/self.page_size))

        for page in range(1,page_num+1):
            if page == 1:
                self.step3(params)
                continue
            LaohuPostComments.post_data['page'] = page
            self.storeposturl(self.post_url, params.originalurl, 
                              self.STEP3, self.post_data)   
        
    #----------------------------------------------------------------------
    def step3(self,params):
        """"""
        soup = BeautifulSoup(params.content,'html5lib')
        items = soup.select('.commertItem')
        comments = []
        for item in items:
            tm = item.select_one('.comment-time').get_text()
            updatetime = getuniformtime(tm)
            comment = item.select_one('.recTxt').get_text()
            if URLStorage.storeupdatetime(params.originalurl, updatetime):
                cmti = CommentInfo()
                cmti.content = comment
                comments.append(cmti)      
        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)            
         
        