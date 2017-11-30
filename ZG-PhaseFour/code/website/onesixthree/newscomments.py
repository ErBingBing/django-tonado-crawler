# coding=utf-8

##############################################################################################
# @file：newscomments.py
# @author：Hedian
# @date：2016/12/05
# @version：Ver0.0.0.100
# @note：网易新闻等获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/01/16
# @note:165-176行，添加了对163.com子站gongyi.163.com的处理
#       150-151行，添加了对163.com子站view.163.com的处理
#       152-153行，添加了对163.com子站cai.163.com的处理
#       146-147行，添加了对163.com子站comment\..*163\.com的处理
# @date:2017/02/08
# @note:第92行url=params.url改为url=proparam.originalurl
#       第120-124行添加了对json文件取不到或异常时的处理

#此newscomments.py停用
##############################################################r################################
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from website.onesixthree.vcomments import VComments
import json
import math


##############################################################################################
# @class：NewsComments
# @author：Hedian
# @date：2016/12/05
# @note：网易新闻获取评论的类，继承于SiteComments类
##############################################################################################
class NewsComments(SiteComments):
    COMMENT_FIRST_URL = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{docID}/comments/newList?limit=1&offset=0'
    COMMENT_URL_EDU = 'http://edu.163.com/comment/0029/education_bbs/I3/vAK13FJI300294III.html'
    COMMENT_FIRST_URL = 'http://sdk.comment.163.com/api/v1/products/{key}/threads/{docid}'
    # COMMENTS_URL = 'http://comment.%s.163.com/api/v1/products/%s/threads/%s/comments/newList?offset=%s&limit=%d&showLevelThreshold=72&headLimit=1&tailLimit=2'
    # COMMENTS_URL = 'http://comment.%s.163.com/api/v1/products/%s/threads/%s/comments/newList?limit=%d&showLevelThreshold=72&headLimit=1&tailLimit=2'
    

    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    limit = 30

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/05
    # @note：NewsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == NewsComments.STEP_1:
            self.common_step1(params)
        if params.step == NewsComments.STEP_2:
            self.common_step2(params)
        if params.step == NewsComments.STEP_3:
            self.common_step3(params)
   
    ##############################################################################################
    # @functions：common_step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/18
    # @note：网易共通方法，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    
    
    
    
    def common_step2(self, proparam):
        # 网易非云阅读的处理
        # Step2: 通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
        # 获取Step1得到的productKey，docId，field
        productKey = proparam.customized['productKey']
        docId = proparam.customized['sid']
        field = proparam.customized['field']
        
        try:
            commentsinfo = json.loads(proparam.content)
            comments_count = float(commentsinfo['newListSize'])
            NewsStorage.setcmtnum(proparam.originalurl, comments_count)
        except:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=proparam.originalurl))
            return

        ### 保存页面评论量
        cmtnum = CMTStorage.getcount(proparam.originalurl, True)
        if cmtnum >= int(comments_count):
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.limit))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        # 拼出获取评论的URL并保存
        for page in range(1, page_num+1, 1):
            if page == 1:
                self.common_step3(proparam)
                continue
            comement_url = NewsComments.COMMENTS_URL % (field, productKey, docId, page * self.limit, self.limit)          
            self.storeurl(comement_url, proparam.originalurl, NewsComments.STEP_2, {'productKey': productKey, 'docId': docId, 'field': field})


    ##############################################################################################
    # @functions：common_step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/18
    # @note：网易共通方法，保存获取的评论。
    ##############################################################################################
    def common_step3(self, proparam):
        # 网易非云阅读处理
        try:
            commentsinfo = json.loads(proparam.content)
        except:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=proparam.originalurl))
            return    
        #commentsinfo = json.loads(proparam.content)
        comments = []

        # 获取评论
        key_comments = 'comments'
        if key_comments in commentsinfo:
            for key in commentsinfo[key_comments].keys():
                try:
                    nickname = commentsinfo[key_comments][key]['user']['nickname']
                except:
                    nickname = 'anonymous'
                if CMTStorage.exist(proparam.originalurl, commentsinfo[key_comments][key]['content'], commentsinfo[key_comments][key]['createTime'], nickname):
                    CMTStorage.storecmt(proparam.originalurl, commentsinfo[key_comments][key]['content'], commentsinfo[key_comments][key]['createTime'], nickname)
                else:
                    break

    ##################################################################################################################
    ### @functions：news_step1
    ### @proparam：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    ### @return：无
    ### @note：
    ##################################################################################################################
    def news_step1(self, params):
        # 网易其他处理
        #field = params.customized['field']
        if self.r.search('^http[s]{0,1}://comment\.(\w+)\..*', params.url):
            field = self.r.parse('^http[s]{0,1}://comment\.(\w+)\..*', params.url)[0]
        else:
            field = self.r.parse('^http[s]{0,1}://(\w+)\..*', params.url)[0]
        if field == 'discovery'  or field == 'data' or field == 'view':
            field = 'news'
        if field == 'cai':
            field = 'sports'

        if field  != 'gongyi':
            if not self.r.search('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                Logger.getlogging().warning('{url} Errorcode:40000 No productKey'.format(url=params.url))
                return
            productKey = self.r.parse('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
            if not self.r.search('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                Logger.getlogging().warning('{url} Errorcode:40000 No docId'.format(url=params.url))
                return
            docId = self.r.parse('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
        else:
            if self.r.search('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                productKey = self.r.parse('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
            else:
                Logger.getlogging().warning('{url}:40000 No productKey'.format(url=params.url))
                productKey = 'a2869674571f77b5a0867c3d71db5856'
            if self.r.search('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                docId = self.r.parse('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
            elif self.r.search('^http[s]{0,1}://.*\.163\.com/.*/(\w+).html', params.originalurl):
                docId = self.r.parse('/(\w+).html', params.originalurl)[0]
            else:
                Logger.getlogging().warning('{url}:40000 No docId'.format(url=params.url))
                return

        commentinfo_url = NewsComments.COMMENT_FIRST_URL.format(key=productKey, docid=docId)

        Logger.getlogging().debug(commentinfo_url)
        self.storeurl(commentinfo_url, params.originalurl, NewsComments.STEP_2,{'productKey': productKey, 'docId': docId, 'field': field})



