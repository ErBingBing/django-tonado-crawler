# coding=utf8
##############################################################################################
# @file：ActoysComments.py
# @author：Han Luyang
# @date：2017/09/11
# @note：AC模玩网获取评论的文件
##############################################################################################
import math
import re
from bs4 import BeautifulSoup as bs
from utility.xpathutil import XPathUtility 
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
##############################################################################################
# @class：ActoysComments
# @author：Han Luyang
# @date：2017/09/07
# @note：AC模玩网获取评论的类，继承于SiteComments
##############################################################################################
class ActoysComments(SiteComments):
    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Han Luyang
    # @date：2017/09/07 
    # @note：初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 20
        self.COMMENT_URL = 'http://bbs.actoys.net/read.php?tid-{tid}-page-{page}.html'
        self.STEP_PAGES = None
        self.STEP_CMTS = 1

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：None
    # @author：Han Luyang
    # @date：2017/09/07
    # @note：根据params.step判断调用step1还是step2
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step == self.STEP_PAGES:
                self.step1(params)
            elif params.step == self.STEP_CMTS:
                self.step2(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        except:
            Logger.printexception
            
    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：None
    # @author：Han Luyang
    # @date：2017/09/07
    # @note：根据传入的url获取帖子包含的所有分页url
    ##############################################################################################     
    def step1(self,params):
        try:
            tid = re.findall('tid[-=](\d+)', params.originalurl)[0]  
            cmtnum = XPathUtility(params.content).getstring('//*[@id="topicRepliesNum"]')
            cmtnum = int(cmtnum)
            #NewsStorage.setcmtnum(params.originalurl, cmtnum)
            dbcmtnum = CMTStorage.getcount(params.originalurl)
            if dbcmtnum >= cmtnum:
                return
            start = int(dbcmtnum /self.page_size) + 1
            end = int(math.ceil(float(cmtnum) /self.page_size))
            if end > start + self.maxpages:
                start = end - self.maxpages
                
            for page in range(end, start-1, -1):
                if page == 1:
                    self.step2(params)
                    continue
                pageUrl = self.COMMENT_URL.format(tid=tid, page=page)
                self.storeurl(pageUrl, params.originalurl, self.STEP_CMTS)
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step2
    # @param： 共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：none
    # @author：Han Luyang
    # @date：2017/09/07
    # @note：从分页页面中取出评论内容及评论时间，并存入
    ##############################################################################################
    def step2(self, params):     
        try:
            soup = bs(params.content,'html5lib')
            cmtsContainer = soup.find_all(attrs={'id':re.compile('readfloor_\d+')})
            timelist = []
            for cmtContainer in cmtsContainer:
                cmtContent = cmtContainer.find(attrs={'class':'f14 mb10'}).get_text()
                cmtPubDate = cmtContainer.find(attrs={'class':'tipTop s6'}).get_text()
                CMTStorage.storecmt(params.originalurl, cmtContent, cmtPubDate, '')
                timelist.append(TimeUtility.getuniformtime(cmtPubDate))
            if not self.isnewesttime(params.originalurl, min(timelist)):
                return True
            return False
        except:
            Logger.printexception()
            

        
            