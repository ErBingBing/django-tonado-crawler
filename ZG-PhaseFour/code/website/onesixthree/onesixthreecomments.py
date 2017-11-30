# encoding=utf-8

##############################################################################################
# @file：onesixthreecomment.py
# @author：Hedian
# @date：2016/11/16
# @version：Ver0.0.0.100
# @note：网易获取评论的文件
##############################################################r################################

from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.gettimeutil import TimeUtility
import json
import math
##############################################################################################
# @class：Comments163
# @author：Hedian
# @date：2016/11/16
# @note：网易获取评论的类，继承于WebSite类
##############################################################################################
class Comments163(SiteComments):
    COMMENTS_URL = 'http://comment.{field}.163.com/api/v1/products/{productkey}/threads/{sid}/comments/newList?offset={itemnum}&limit={itemlimit}&showLevelThreshold=72&headLimit=1&tailLimit=2'
    CLICKNUM_URL = 'http://sdk.comment.163.com/api/v1/products/{key}/threads/{docid}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4
    limit = 30

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Hedian
    # @date：2016/11/16
    # @note：Comments163类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Hedian
    # @date：2016/11/16
    # @note：Step1：通过共通模块传入的html内容获取到productKey，docId，拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        if params.step == Comments163.STEP_1:
            self.common_step1(params)
        if params.step == Comments163.STEP_2:
            self.common_step2(params)
        if params.step == Comments163.STEP_3:
            self.common_step3(params)
        if params.step == Comments163.STEP_4:
            self.setclicknum(params)
            
            
    def common_step1(self, params):
        Logger.getlogging().info(params.originalurl)
        try:
            #field = self.r.parse('^http://(\w+)\.163.com?', params.originalurl)[0]
            field = params.originalurl.split('//')[-1].split('.163')[0].split('.')[-1]
            sid = params.originalurl.split('/')[-1].split('.')[0]
            #productkey = self.r.parse('\"productKey\" : \"(\w+)\"',params.content)[0]
            productkey = self.r.getid('productKey',params.content)
            commentinfo_url = Comments163.COMMENTS_URL.format(field=field, sid=sid, productkey=productkey, itemnum=0, itemlimit=self.limit)
            self.storeurl(commentinfo_url, params.originalurl, Comments163.STEP_2,{'field': field,
                                                                                    'sid': sid,
                                                                                    'productkey': productkey})             
        except:
            Logger.printexception()

        if NewsStorage.getclicknum(params.originalurl) <= 0:
            if self.r.search('^http[s]{0,1}://comment\.(\w+)\..*', params.url):
                field = self.r.parse('^http[s]{0,1}://comment\.(\w+)\..*', params.url)[0]
            else:
                field = self.r.parse('^http[s]{0,1}://(\w+)\..*', params.url)[0]
            if field == 'discovery' or field == 'data' or field == 'view':
                field = 'news'
            if field == 'cai':
                field = 'sports'

            if field != 'gongyi':
                if not self.r.search('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}',
                                     params.content):
                    Logger.getlogging().warning('{url} Errorcode:40000 No productKey'.format(url=params.url))
                    return
                productKey = \
                self.r.parse('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
                if not self.r.search('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                    Logger.getlogging().warning('{url} Errorcode:40000 No docId'.format(url=params.url))
                    return
                docId = self.r.parse('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
            else:
                if self.r.search('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                    productKey = \
                    self.r.parse('[\s\'\"]{1}productKey[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
                else:
                    Logger.getlogging().warning('{url}:40000 No productKey'.format(url=params.url))
                    productKey = 'a2869674571f77b5a0867c3d71db5856'
                if self.r.search('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content):
                    docId = \
                    self.r.parse('[\s\'\"]{1}docId[\'\"]{0,1}\s*:\s*[\'\"]{0,1}(\w+)[,\'\"]{1}', params.content)[0]
                elif self.r.search('^http[s]{0,1}://.*\.163\.com/.*/(\w+).html', params.originalurl):
                    docId = self.r.parse('/(\w+).html', params.originalurl)[0]
                else:
                    Logger.getlogging().warning('{url}:40000 No docId'.format(url=params.url))
                    return

            clickurl = self.CLICKNUM_URL.format(key=productKey, docid=docId)
            self.storeurl(clickurl, params.originalurl, self.STEP_4)

            
    def common_step2(self, params):
        productkey = params.customized['productkey']
        sid = params.customized['sid']
        field = params.customized['field']
        commentsinfo = json.loads(params.content)
        comments_count = commentsinfo.get('newListSize',0)
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        # 保存页面评论量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= int(comments_count):
            return
        max = int(math.ceil(float(comments_count-cmtnum) / self.limit))
        if max > self.maxpages:
            max= self.maxpages
        # 拼出获取评论的URL并保存
        for page in range(1, max+1, 1):
            if page == 1:
                self.common_step3(params)
                continue
            comement_url = Comments163.COMMENTS_URL.format(field=field, sid=sid, productkey=productkey, itemnum=page * self.limit, itemlimit=self.limit)
            self.storeurl(comement_url, params.originalurl, Comments163.STEP_3)
        
    ##############################################################################################
    # @functions：common_step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/18
    # @note：网易共通方法，保存获取的评论。
    ##############################################################################################
    def common_step3(self, params):
            # 网易非云阅读处理
        try:
            commentsinfo = json.loads(params.content)
        except:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return    
        key_comments = 'comments'
        for key in commentsinfo.get(key_comments,[]):
            nickname = commentsinfo[key_comments][key]['user'].get('nickname','anonymous')
            content = commentsinfo[key_comments][key]['content']
            curtime = commentsinfo[key_comments][key]['createTime']
            if not CMTStorage.exist(params.originalurl,content, curtime, nickname):
                CMTStorage.storecmt(params.originalurl,content, curtime, nickname)
    def setclicknum(self,params):
        try:
            jsondate = json.loads(params.content)
            todayplaynum = jsondate['cmtVote']
            publishdate = jsondate['createTime']
            NewsStorage.setclicknum(params.originalurl, todayplaynum)
            NewsStorage.setpublishdate(params.originalurl, TimeUtility.getuniformtime(publishdate))
        except:
            Logger.printexception()

  

