# coding=utf-8

##############################################################################################
# @file：jcomments.py
# @author：Hedian
# @date：2016/12/05
# @version：Ver0.0.0.100
# @note：网易荐新闻获取评论的文件
##############################################################r################################
from log.spiderlog import Logger

from website.common.comments import SiteComments
from website.onesixthree.newscomments import NewsComments
from website.onesixthree.onesixthreecomments import Comments163
import json


##############################################################################################
# @class：JComments
# @author：Hedian
# @date：2016/12/05
# @note：网易荐新闻获取评论的类，继承于SiteComments类
##############################################################################################
class JComments(SiteComments):
    # COMMENT_FIRST_URL = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{docID}/comments/newList?limit=1&offset=0'
    COMMENT_URL = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{docID}/comments/newList?limit={limit}&offset={offset}'
    J_STEP_1 = None
    J_STEP_2 = 'J_STEP_2'
    J_STEP_3 = 'J_STEP_3'

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/05
    # @note：VideoComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        if params.step == JComments.J_STEP_1:
            self.j_step1(params)
        if params.step == JComments.J_STEP_2:
            self.j_step2(params)
        if params.step == JComments.J_STEP_3:
            Comments163(self).common_step3

    ####################################################################################
    # @functions：getrecommendnewsfieldurl
    # @param：原始url
    # @return：获取field字段的url，docid
    # @author：Hedian
    # @date：2016/11/18
    # @note：根据原始url，得到频道值和doci
    ##############################################################################################
    def getrecommendnewsfieldurl(self, url):
        # 根据原始url,获取channelvalue和docid
        # http://j.news.163.com/#detail/2/C22OL63405178D8P
        value = self.r.parse('^http://j.news.163.com/#detail/(\d+)/(\w+)', url)[0]
        channelvalue = value[0]
        docid = value[1]
        fieldurl = 'http://j.news.163.com/hy/doc.s?type={channelvalue}&channel={channelvalue}&hash=&refer=http%3A//j.news.163.com/&docid={docid}'.format(channelvalue = channelvalue, docid = docid)
        return fieldurl, docid

    ##############################################################################################
    # @functions：recommendnewstep1_5
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/11/18
    # @note：获取荐新闻的field字段名，并更新
    ##############################################################################################
    def j_step2(self, proparam):
        Logger.getlogging().info("Comments163.STEP_1_5")
        #http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/C22OL63405178D8P
        productKey = proparam.customized['productKey']
        docId = proparam.customized['docId']
        field = proparam.customized['field']
        try:
            commentsinfo = json.loads(proparam.content)
            ugcarr = commentsinfo['ugc'].split(',')
        except:
            Logger.getlogging().warning('{0}:30000 No comments'.format(proparam.originalurl))
            return
        if len(ugcarr) < 3:
            if ugcarr[0].strip() == 'comment_bbs':
                # 没有评论，直接返回
                return
            ugcval = ugcarr[0].split('_')
            field = ugcval[0].strip()
        else:
            field = ugcarr[2].strip()
        commentinfo_url = 'http://sdk.comment.163.com/api/v1/products/{key}/threads/{docid}'.format(key=productKey, docid=docId)
        self.storeurl(commentinfo_url, proparam.originalurl, JComments.J_STEP_3, {'productKey': productKey, 'docId': docId, 'field': field})

    ################################################################################################################
    # @functions：video_step1
    # @proparam：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：
    ################################################################################################################
    def j_step1(self, params):
        # 网易荐新闻处理
        # http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/C22OL63405178D8P
        commentinfo_url, docId = self.getrecommendnewsfieldurl(params.originalurl)
        productKey = 'a2869674571f77b5a0867c3d71db5856'
        self.storeurl(commentinfo_url, params.originalurl, JComments.J_STEP_2,
                      {'productKey': productKey, 'docId': docId, 'field': 'j'})



