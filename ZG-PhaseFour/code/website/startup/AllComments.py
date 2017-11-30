# encoding=utf-8
##############################################################################################
# @file：mofangcomments.py
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：评论获取
##############################################################################################

import json
import re
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from log.spiderlog import Logger
import traceback
from storage.urlsstorage import URLStorage

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/11/20
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    COMMENTS_URL = 'http://news.startup-partner.com/ajax/ajax_action.php?action=comment&callback=data&post_id=%s&type=list'
    PAGE_SIZE = 50
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

        #----------------------------------------------------------------------
        ##############################################################################################
        # @functions：process
        # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
        # @return：Step1：获取评论的首页url
        #          Step2：获取评论的所有url
        #          Step3: 抽出的评论和最新评论的创建时间
        # @author：Merlin.W.ouyang
        # @date：2016/11/20
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：获取所有评论的那个URL页面
        #        Step3：由于评论不是按照时间排序，所以都取出来进行实践排序，通过实践判断获取增量评论
        ##############################################################################################   
        
    def process(self, params):
        try:
            if params.step is AllComments.STEP_1:
                key = int(re.findall("\d+",params.url.split("/")[-1])[0])
                comments_url = AllComments.COMMENTS_URL % (key)
                self.storeurl(comments_url, params.originalurl, AllComments.STEP_2, 
                              {'key':key})
            elif params.step is AllComments.STEP_2:
                jsoncontent = self.r.parse('data\((.*?)\)',params.content)[0]
                comments=json.loads(jsoncontent) 
                pcontent=[]
                ptime=[]
                index=0
                for index in range(0,len(comments['comments'])):
                    pcontent.append(comments['comments'][index]['comment_content'])
                    ptime.append(comments['comments'][index]['comment_date'])
                dataresult ={}   
                for i in range(len(pcontent)):
                    dataresult[ptime[i]] = pcontent[i]
                comments = []              
                dataresult=sorted(dataresult.iteritems(),key=lambda dataresult:dataresult[0],reverse=True)
                for k in range(0,len(dataresult)):
                    if URLStorage.storeupdatetime(params.originalurl, dataresult[k][0]): 
                        cmti=CommentInfo()
                        cmti.content=dataresult[k][1]
                        comments.append(cmti)
                self.commentstorage.store(params.originalurl, comments)              
        except Exception ,e:
            traceback.print_exc()
            Logger.getlogging().error(e.message)
            