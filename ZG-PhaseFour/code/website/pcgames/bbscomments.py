# encoding=utf-8
##############################################################################################
# @file：bbscomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/26
# @note：太平洋游戏（PCG）论坛评论获取
##############################################################################################

import json
import math
import urllib
import re
from bsddb import db
from utility.httputil import HttpUtility
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from log.spiderlog import Logger
import traceback
import time
import datetime
from lxml import etree
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
from utility.gettimeutil import TimeUtility

##############################################################################################
# @class：BBSComments
# @author：Merlin.W.OUYANG
# @date：2016/11/26
# @note：获取评论的类，继承于SiteComments类
##############################################################################################
class BBSComments(SiteComments):
    COMMENTS_URL = 'http://bbs.pcgames.com.cn/%s.html'
    PAGE_SIZE = 50
    STEP_1 = None
    STEP_2 = 2

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/11/26
    # @note：太平洋游戏（PCG）论坛类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.pagelimit = self.maxpages
        self.website = parent.website

    #----------------------------------------------------------------------
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Merlin.W.ouyang
    # @date：2016/11/26
    # @note：Step1：根据URL获取第一页评论的URL，进入step2
    #        Step2：获取所有评论的那个URL页面
    #        Step3：由于评论不是按照时间排序，所以都取出来进行实践排序，通过实践判断获取增量评论
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is self.STEP_1:
                soup = BeautifulSoup(params.content,'html5lib')
                body = soup.find(attrs={'class':'post_message post_first'})
                if body:
                    NewsStorage.setbody(params.originalurl, body.get_text().strip())
                else:
                    Logger.getlogging().debug('{url}:30000!'.format(url=params.originalurl))        
                keyvalue = params.url.split("/")[-1].split(".")[0]
                
                page = soup.select('.pager > a')
        
                if len(page) <=2:
                    page = 1
                else:
                    page = page[-2].get_text()
                    page = int(re.findall('\d+',page)[0])
                    
                if self.pagelimit:
                    if int(page) > self.pagelimit:
                        Logger.getlogging().warning('the pageMaxNumber is shutdown to {0}'.format(self.pagelimit))
                        page = self.pagelimit    
                        
                for pg in range(1,int(page+1)):
                    comments_url =self.COMMENTS_URL % (keyvalue+'-'+str(pg))
                    self.storeurl(comments_url, params.originalurl, self.STEP_2,{'page':pg,'pagetotal':page})
                
            elif params.step is self.STEP_2:
                #self.get_comments(params)
                page = params.customized['page']
                soup = BeautifulSoup(params.content,'html5lib')
                posts = soup.select('.post_wrap')
                if not posts:
                    Logger.getlogging().debug('{url}:30000!'.format(url=params.originalurl)) 
                    return
                for post in posts:
                    post_msg = post.select_one('.post_message').get_text()
                    post_msg = ''.join(post_msg.split())
                    # class ="user-42845238 post_time needonline " > 发表于 2017-07-27 23:53
                    post_time = post.find(attrs={'class':re.compile('user-.+post_time needonline')}).get_text()
                    curtime = TimeUtility.getuniformtime(post_time)
                    content = post_msg.strip()
                    try:
                        # class ="user-40693231 needonline" > Akemi隅晖 < / a >
                        nick = post.find(attrs={'class': re.compile('user-.+ needonline')}).get_text()
                    except:
                        nick = 'nickname'
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                    
        except:
            Logger.printexception()

                       
            
