# coding=utf-8

##############################################################################################
# @file：laohuComments.py
# @author：HuBorui
# @date：2016/11/30
# @version：Ver0.0.0.100
# @note：老虎游戏论坛获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################r################################

import math

from log.spiderlog import Logger
from utility.xpathutil import XPathUtility
from utility.gettimeutil import getuniformtime
from website.common.comments import SiteComments
from utility.regexutil import RegexUtility
from website.laohu.laohupostcomments import LaohuPostComments
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from utility.bbs2commom import CommenComments

########################################################################
class LaohuComments_all(SiteComments):
    """"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        SiteComments.__init__(self)
    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if self.r.search('http[s]{0,1}://ff\.laohu\.com.*',params.originalurl):
            LaohuPostComments(self).process(params)
        elif self.r.search('http[s]{0,1}://bbs\.laohu\.com.*',params.originalurl):
            LaohuComments(self).process(params)
        else:
            Logger.getlogging().debug('{url}:40000  Not in task'.format(params.originalurl))
            Logger.log(params.originalurl,'40000')
            return
        
 
##############################################################################################
# @class：laohuComments
# @author：HuBorui
# @date：2016/11/29
# @note：老虎游戏论坛获取评论的类，继承于SiteComments类
##############################################################################################
class LaohuComments(SiteComments):
    # 评论第一页规则
    COMMENTS_URL = 'http://member.laohu.com/comment/show/?token=%s&oder=new'
    PAGE_SIZE = 15.0
    BBS_URL_REG = '^http://bbs\.laohu\.com\/\w+-\d+-(\d+)-\d+\.html'
    BBS_TITLE = ''
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_2_BBS = '2_bbs'
    STEP_3_BBS = '3_bbs'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：HuBorui
    # @date：2016/11/29
    # @note：老虎游戏论坛类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self,parent=None):
        SiteComments.__init__(self)
        self.r = RegexUtility()
        # self.basicstorage = BaseInfoStorage()
        # self.commentstorage = CommentsStorage()
        if parent:
            self.website = parent.website         

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：laohuComments入口函数，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        if params.step is None:
            self.step1(params)
        elif params.step == LaohuComments.STEP_2:
            self.step2(params)
        elif params.step == LaohuComments.STEP_2_BBS:
            self.step2bbs(params)
        elif params.step == LaohuComments.STEP_3:
            self.step3(params)
        elif params.step == LaohuComments.STEP_3_BBS:
            self.step3bbs(params)
        
        else:
            return

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @updateAuthor:Ninghz
    # @updateDate:2016/12/14
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("LaohuComments.STEP_1")
        #1. 根据输入原始url, 得到网站的子域名
        field = self.r.parse('^http://(\w+)\.laohu\.com/.*', params.originalurl)[0]
        # 论坛
        if field == 'bbs':
            # 拼接获取uniqid的url
            self.storeurl(params.originalurl, params.originalurl, LaohuComments.STEP_2_BBS,{'field': field})
        else:
            # 非论坛页面  http://ff.laohu.com/201612/215072.html
            xhtml = XPathUtility(html=params.content)
            token = xhtml.getlist('// *[ @ id = "t_token"]')[0]
            sourceId = self.r.getid('source_id', params.content, '\s*=\s*')
            # 拼接第一页评论url
            COMMENTS_URL = 'http://member.laohu.com/comment/show/?token=%s&oder=new'
            comments_url = LaohuComments.COMMENTS_URL % (token)
            # 通知下载平台，根据评论url获取第一页评论内容
            self.storeurl(comments_url, params.originalurl, LaohuComments.STEP_2, {'token' : token, 'sourceId':sourceId})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/14
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("LaohuComments.STEP_2")
        token = params.customized['token']
        sourceId = params.customized['sourceId']
        xhtml = XPathUtility(html=params.content)
        # 网友评论(32)
        countstr = xhtml.getlist('//*[@class="filter-by-type"]')[0]
        comment_counts = int(countstr[5:countstr.__len__()-1])
        if comment_counts:
            NewsStorage.setcmtnum(params.originalurl, comment_counts)
        if comment_counts == 0:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        # 判断增量
        if cmtnum >= comment_counts:
            #Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        page_num = int(math.ceil(float(comment_counts - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        # 获取第一页评论内容
        self.getComments(params)
        if comment_counts > 15:
            # 循环拼接评论url，提交下载平台获取评论数据
            COMMENTS_URL = 'http://member.laohu.com/comment/ajax?page=%d&token=%s&order=new'
            for page in range(2, page_num + 1, 1):
                commentUrl = LaohuComments.COMMENTS_URL % (page, sourceId)
                self.storeurl(commentUrl, params.originalurl, LaohuComments.STEP_3, {'token' : token, 'sourceId':sourceId})


    ##############################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2bbs(self, params):
        Logger.getlogging().info("LaohuComments.STEP_2_BBS")
             
        if self.r.parse('^http://bbs\.laohu\.com\/\w+-(\d+)-\d+-\d+\.html',params.originalurl):
            #S1
            field = params.customized['field']
            # 通过xpath, 从页面上获取页面总数
            # lastpg = CommenComments.gettotalpages(params.content)
            lastpg = int(self.r.parse('<span title=".*">(.*?)</span>',params.content)[0].split('/')[1].split(' ')[1])
            if lastpg is None:
                return
    
            # 当前评论页码
            pg = self.r.parse(self.BBS_URL_REG, params.url)[0]
    
            # 获取当前页评论
            params.customized['lastpg'] = lastpg
            CommenComments.getpagecomments(self, params, self.BBS_URL_REG)
    
            # 如果只有1页，后续处理不要
            if int(lastpg) == 1:
                return
    
            # 对于S1, 需要展开获取所有评论
            urlArr = params.originalurl.split('-')
            if len(urlArr) != 4:
                return
            for page in range(1, lastpg + 1, 1):
                if page == int(pg):
                    continue
                commentUrl = urlArr[0] + '-' + urlArr[1] + '-' + str(page) + '-' + urlArr[3]
                Logger.getlogging().debug(commentUrl)
                self.storeurl(commentUrl, params.originalurl, LaohuComments.STEP_3_BBS,
                              {'field': field, 'lastpg': lastpg})
        else:
            #特殊网址
            CommenComments.getpagecomments2(self, params)
            
            
                

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/14
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("LaohuComments.STEP_3")
        # 翻页的评论url返回错误，无法获取第二页之后的评论内容


    ##############################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：HuBorui
    # @date：2016/11/30
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3bbs(self, params):
        Logger.getlogging().info("LaohuComments.STEP_3_BBS")
        CommenComments.getpagecomments(self, params, self.BBS_URL_REG)

    def getComments(self, params):
        xhtml = XPathUtility(html=params.content)
        commentinfo = xhtml.getlist('//*[@class="recTxt"]')
        updatetimes = xhtml.getlist('//*[@class="comment-time"]')
        comments = []
        for index in range(0, commentinfo.__len__()):
            curtime = TimeUtility.getuniformtime(updatetimes[index][1:updatetimes[index].__len__() - 1])
            content = commentinfo[index]
            nick = 'nick'
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

        if len(comments) > 0:
            self.commentstorage.store(params.originalurl, comments)