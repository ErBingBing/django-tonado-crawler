## encoding=utf-8
###############################################################################################
## @file：pcgamescomments.py
## @author：Merlin.W.OUYANG
## @date：2016/12/6
## @note：评论获取,使用的是第三方多说的cms插件
###############################################################################################

#import re
#import urllib
#import json
#import math
#from utility.timeutility import TimeUtility
#from utility.common import Common
#from storage.cmtstorage import CMTStorage
#from storage.newsstorage import NewsStorage
#from utility.timeutility import TimeUtility
#from log.spiderlog import Logger
#from website.common.comments import SiteComments
#from utility.xpathutil import XPathUtility

###############################################################################################
## @class：AllComments
## @author：Merlin.W.OUYANG
## @date：2016/12/6
## @note：获取评论的类，继承于WebSite类
###############################################################################################
#class AllComments(SiteComments):
    #COMMENTS_URL = 'http://gamelook.duoshuo.com/api/threads/listPosts.json?thread_key=%s&page=%d&order=desc'
    #PAGE_SIZE = 50
    #STEP_1 = None
    #STEP_2 = 2
    #STEP_3 = 3

    ###############################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @author：Merlin.W.OUYANG
    ## @date：2016/12/6
    ## @note：AllComments类的构造器，初始化内部变量
    ###############################################################################################
    #def __init__(self):
        #SiteComments.__init__(self) 

    #def process(self, params):
        #try:
            #if params.step is self.STEP_1:
                #self.step1(params)
            #elif params.step == self.STEP_2:
                #self.step2(params)
            #elif params.step == self.STEP_3:
                #self.step3(params)
        #except:
            #Logger.printexception()	


    ##----------------------------------------------------------------------
    #def step1(self,params):
        #threadid = self.r.getid('data-thread-key', params.content, split='=')
        #comments_url = AllComments.COMMENTS_URL % (threadid, 1)
        #self.storeurl(comments_url, params.originalurl, AllComments.STEP_2, {'threadid':threadid,'pageno':1})  
    
    ##----------------------------------------------------------------------
    #def step2(self, params):
        #comments = json.loads(params.content)       
        #pagetotal= int(comments['cursor']['pages'])
        #comments_url = AllComments.COMMENTS_URL % (params.customized['threadid'],params.customized['pageno'])
        #self.storeurl(comments_url, params.originalurl, AllComments.STEP_3, 
                      #{'threadid':params.customized['threadid'], 
                       #'pageno':params.customized['pageno'],
                       #'totalpage':pagetotal})     

    ##----------------------------------------------------------------------
    #def step3(self, params):
        #if params.customized['pageno']<=params.customized['totalpage']:
            #comments = json.loads(params.content)
            ##roll=len(comments['response'])
            #ptimer=[]
            #pcontent=[]
            #for key in comments['parentPosts'].keys():
                #ptime = comments['parentPosts'][key]['created_at']
                #ptime = ptime.split("+")[0]
                #ptime = ptime.replace("T"," ")
                #ptimer.append(datetime.datetime.strptime(ptime,'%Y-%m-%d %H:%M:%S'))
                #pcontent.append(comments['parentPosts'][key]['message'])
            #for ctime in range(0,len(ptimer)):
                #ptimer[ctime]=datetime.datetime.strptime(str(ptimer[ctime]),'%Y-%m-%d %H:%M:%S')
            #index=0
            #comments = []
            #complete = False
            #for comment in pcontent:
                #cmti = CommentInfo()
                #cmti.content = comment
                #if URLStorage.storeupdatetime(params.originalurl, str(ptimer[index])):
                    #comments.append(cmti)
                #else:
                    #complete = True
                    #break;
                #index =index+ 1
            #self.commentstorage.store(params.originalurl, comments)
            #if not complete:
                #comments_url = AllComments.COMMENTS_URL % (params.customized['threadid'], params.customized['pageno']+1)
                #self.storeurl(comments_url, params.originalurl, AllComments.STEP_3, 
                              #{'threadid':params.customized['threadid'], 
                               #'pageno':params.customized['pageno']+1,
                               #'totalpage':params.customized['totalpage']})
