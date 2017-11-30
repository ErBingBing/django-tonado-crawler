# encoding=utf-8
##############################################################################################
# @file：pcgamescomments.py
# @author：Merlin.W.OUYANG
# @date：2016/12/13
# @note：评论获取
##############################################################################################

import json
import re
from website.common.comments import SiteComments
from storage.commentsstorage import CommentInfo
from utility.timeutility import TimeUtility 
from log.spiderlog import Logger
import traceback
from storage.urlsstorage import URLStorage

##############################################################################################
# @class：AllComments
# @author：Merlin.W.OUYANG
# @date：2016/12/13
# @note：获取评论的类，继承于WebSite类
##############################################################################################
class AllComments(SiteComments):
    AID_URL = 'http://himg2.huanqiu.com/js/commentiframe.js?aid=%s&app=cms&type=cms'
    KEYID_URL = 'https://commentn.huanqiu.com/api/v2/async?a=comment&m=source_info&appid=%s&sourceid=%s&url=%s'
    COMMENTS_URL = 'https://commentn.huanqiu.com/api/v2/async?a=comment&m=comment_list&sid=%s&n=15&p=%s&appid=%s'
    PAGE_SIZE = 15
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4
    STEP_5 = 5

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Merlin.W.OUYANG
    # @date：2016/12/13
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
        # @date：2016/12/13
        # @note：Step1：根据URL获取第一页评论的URL，进入step2
        #        Step2：获取所有评论的那个URL页面
        #        Step3：由于评论不是按照时间排序，所以都取出来进行实践排序，通过实践判断获取增量评论
        ##############################################################################################   
        
    def process(self, params):
        try:
            if params.step is AllComments.STEP_1:
                aid = re.findall("\d+",params.url.split("/")[-1])[0]
                aid_url = AllComments.AID_URL % (aid)
                self.storeurl(aid_url, params.originalurl, AllComments.STEP_2, 
                                  {'aid':aid})                
            elif params.step is AllComments.STEP_2:
                cms_id = re.findall('appidArr \= \[\"cms\|(.+?)",',str(params.content))[0];
                cms_url = AllComments.KEYID_URL % (cms_id, params.customized['aid'], params.originalurl)
                self.storeurl(cms_url, params.originalurl, AllComments.STEP_3,
                              {'aid':params.customized['aid'],
                               'cmsid':cms_id})
            elif params.step is AllComments.STEP_3:
                comments=json.loads(params.content)
                sid=comments['data']['_id']
                comment_url = AllComments.COMMENTS_URL % (sid, '1', params.customized['cmsid'])
                self.storeurl(comment_url, params.originalurl, AllComments.STEP_4,
                              {'sid':sid,
                               'page':'1',
                               'cmsid':params.customized['cmsid']})
            elif params.step is AllComments.STEP_4:
                comments=json.loads(params.content)
                try:
                    comment=[]
                    index=0
                    for index in range(0,len(comments['data'])):
                        ctime=TimeUtility.getuniformtime2(comments['data'][index]['ctime'])
                        if URLStorage.storeupdatetime(params.originalurl, str(ctime)):
                            cmti=CommentInfo()
                            cmti.content=comments['data'][index]['content']
                            comment.append(cmti)
                    self.commentstorage.store(params.originalurl, comment)
                    comment_url = AllComments.COMMENTS_URL % (params.customized['sid'], str(int(params.customized['page'])+1), params.customized['cmsid'])
                    self.storeurl(comment_url, params.originalurl, AllComments.STEP_4,
                                  {'sid':params.customized['sid'],
                                   'page':str(int(params.customized['page'])+1),
                                   'cmsid':params.customized['cmsid']})
                except:
                    return
                
        except Exception ,e:
            traceback.print_exc()
            Logger.getlogging().error(e.message)
            