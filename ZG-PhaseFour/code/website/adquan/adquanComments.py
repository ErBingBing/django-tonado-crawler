# encoding=utf8

##############################################################################################
# @file：AdquanComments.py
# @author：Liuyonglin
# @date：2016/12/08
# @version：Ver0.0.0.100
# @note：广告门获取评论的文件
##############################################################################################

import traceback

import re
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from utility.xpathutil import XPathUtility
from  bs4 import BeautifulSoup

##############################################################################################
# @class：AdquanComments
# @author：Liuyonglin
# @date：2016/12/08
# @note：广告门获取评论的类，继承于WebSite类
##############################################################################################
class AdquanComments(SiteComments):
    COMMENT_URL = 'http://creative.adquan.com/show/{docurl}'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：AdquanComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liuyonglin
    # @date：2016/12/08
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is AdquanComments.STEP_1:
                soup = BeautifulSoup(params.content, 'html5lib')
                divs = soup.select('#comments > .comment_inner')
                NewsStorage.setcmtnum(params.url, len(divs))
                for div in divs:
                    content = div.select_one('.reviews_con').get_text()
                    pubtime = div.select_one('.reviews_time').get_text()
                    nick = div.select_one('.reviews_name').get_text()
                    CMTStorage.storecmt(params.url, content, pubtime, nick)
        except:
            Logger.printexception()

    ###############################################################################################
    ## @functions：step1
    ## @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    ## @return：无
    ## @author：Liuyonglin
    ## @date：2016/12/8
    ## @note：根据主页获取评论页，传入评论页，获取评论数
    ###############################################################################################
    #def step1(self, params):
        #Logger.getlogging().info("AdquanComments.STEP_1")
        #xparser = XPathUtility(params.content)
        ##get body
        ##body = xparser.getcontent('//*[@class="con_Text"]/div[1]')
        ##NewsStorage.setbody(params.originalurl, body)
        ###get title
        ##title = xparser.gettitle('//*[@class="text_title"]')
        ##NewsStorage.settitle(params.originalurl, title)
        ###get pubtime
        ##pubtime = xparser.gettime('//*[@class="con1"]')
        ##NewsStorage.setpublishdate(params.originalurl, pubtime)
        ###get clicknumber
        ##clicknum = xparser.xpath('//*[@class="text_time2"]/span[3]')
        ##NewsStorage.setclicknum(params.originalurl , clicknum)
        ##get cmtnumber
        #soup = BeautifulSoup(params.content, 'html5lib')
        #cmt = soup.select_one('#comments')
        #if cmt:
            #divs = cmt.find(attrs={'class':re.compile('reviews_con')})
            #comments_count = len(divs)
        
        ## 判断增量
        #cmtnum = CMTStorage.getcount(params.originalurl, True)
        #if cmtnum >= comments_count:
            #return
        #NewsStorage.setcmtnum(params.originalurl, comments_count)

        #self.storeurl(params.originalurl, params.originalurl, AdquanComments.STEP_3)

    ###############################################################################################
    ## @functions：step3
    ## @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    ## @return：无
    ## @author：Liuyonglin
    ## @date：2016/12/8
    ## @note：根据输入的html(json文件），得到评论
    ###############################################################################################
    #def step3(self, params):
        ## Step3: 通过Step2设置的url，得到所有评论，抽取评论
        #xparser = XPathUtility(params.content)
        #commentsinfo = xparser.getcomments('//*[@class="reviews_con"]')
        #commentstime = self.r.parse(ur'(\d+-\d+-\d+)</p>', params.content)
        #comments = []

        #for index in range(0, len(commentstime), 1):
            #CMTStorage.storecmt(params.originalurl, commentsinfo[index], commentstime[index], '')
            ##cmti = CommentInfo()
            ## 提取评论内容
            ##cmti.content = commentsinfo[index]
            ## 提取时间
            ##publicTime = commentstime[index]
            ##tm = TimeUtility.getuniformtime(TimeUtility.getuniformtime(publicTime, u'%Y-%m-%d'))
            ##if URLStorage.storeupdatetime(params.originalurl, tm):
                ##comments.append(cmti)
            

        #if len(comments) > 0:
            ## 保存获取的评论
            #self.commentstorage.store(params.originalurl, comments)