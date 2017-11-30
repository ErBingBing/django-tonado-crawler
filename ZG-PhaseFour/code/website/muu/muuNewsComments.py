# encoding=utf8

##############################################################################################
# @file：muuNewsComments.py
# @author：Liyanrui
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：漫悠悠漫画网漫画页新闻页获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################################################
import traceback
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
import math
from website.tencent.tencent import TencentComments

##############################################################################################
# @class：muuNewsComments
# @author：Liyanrui
# @date：2016/12/12
# @note：漫悠悠漫画网漫画页新闻页获取评论的类，继承于WebSite类
##############################################################################################
class muuNewsComments(SiteComments):
    COMMENT_URL ='http://www.muu.com.cn/commentList.do?pageNo=%d&sId=%s&sClass=002'
    COMMENT_URL_CLASS2 = 'http://www.muu.com.cn/commentList.do?pageNo=%d&sId=%s&sClass=002&wClass=006'
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/12/12
    # @note：漫悠悠漫画网漫画页新闻页类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Liyanrui
    # @date：2016/12/12
    # @note：Step1：通过共通模块传入的html内容获取到docurl,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        # muu网站改版，目前只有两种类型url，目前只处理第二种类型
        # 1.http://www.manhuadao.cn/Home/ComicDetail?id=58ddae3e27a7c1392c220ebf
        # 2.http://ac.qq.com/Comic/comicInfo/id/541327
        if self.r.search('^http[s]{0,1}://ac\.qq\.com/Comic/.*', params.originalurl):
            TencentComments(self).process(params)
        else:
            return

        # try:
        #     if params.step is muuNewsComments.STEP_1:
        #         #Step1: 通过得到docurl，得到获取评论的首页url参数。
        #         articleId = self.r.parse('^http://www\.muu\.com\.cn/\w+/(\d+)\.html', params.originalurl)[0]
        #         # 获取首页评论url
        #         url = muuNewsComments.COMMENT_URL % (1, articleId)
        #         self.storeurl(url, params.originalurl, muuNewsComments.STEP_2, {'articleId': articleId})
        #     elif params.step == muuNewsComments.STEP_2:
        #         articleId = params.customized['articleId']
        #         # 取得总件数
        #         comment_count = float(self.r.parse(ur'value="(\d+)"', params.content)[1])
        #         if comment_count:
        #             NewsStorage.setcmtnum(params.originalurl, comment_count)
        #         if comment_count == 0:
        #             return
        #         # 判断增量
        #         cmtnum = CMTStorage.getcount(params.originalurl, True)
        #         if cmtnum >= comment_count:
        #             return
        #         # 获取页数
        #         page = int(math.ceil(comment_count -  cmtnum/ muuNewsComments.PAGE_SIZE))
        #         # 获得url列表
        #         for page in range(1, page + 1, 1):
        #             url = muuNewsComments.COMMENT_URL % (page, articleId)
        #             self.storeurl(url, params.originalurl, muuNewsComments.STEP_3)
        #             # 获得戳阅读模式url列表
        #             url = muuNewsComments.COMMENT_URL_CLASS2 % (page, articleId)
        #             self.storeurl(url, params.originalurl, muuNewsComments.STEP_4)
        #     elif params.step == muuNewsComments.STEP_3:
        #         # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        #         Logger.getlogging().info("params.step == 3")
        #         # 取得所有评论
        #         comments = self.r.parse(ur'\$\("#text_".+?\)\.html\(replace_em\(.+?\)\)', params.content)
        #         # 取得所有评论时间
        #         commenttimes = self.r.parse(ur'<span name="createTime">(.+?)</span>', params.content)
        #         # 取得所有用户名
        #         nicks = self.r.parse(ur'<span name="createTime">(.+?)</span>', params.content)
        #         # commentsInfo = []
        #         # 取得所有评论
        #         # for index in range(0, int(len(comments)), 1):
        #         #     # 提取时间
        #         #     if URLStorage.storeupdatetime(params.originalurl, commenttimes[index]):
        #         #         cmti = CommentInfo()
        #         #         cmti.content = self.r.parse(ur"replace_em((.*))", comments[index])[0][0]
        #         #         commentsInfo.append(cmti)
        #         #     # 保存获取的评论
        #         # if len(commentsInfo) > 0:
        #         #     self.commentstorage.store(params.originalurl, commentsInfo)
        #     elif params.step == muuNewsComments.STEP_4:
        #         commentsInfo = []
        #         xparser = XPathUtility(params.content)
        #         # 获取评论
        #         comments = xparser.xpath('/html/body/li/div/p')
        #         # 获取评论时间
        #         commentTime = self.r.parse(ur' 回复于([\s\S]+?)</span>', params.content)
        #         # 取得所有评论
        #         for index in range(0, int(len(comments)), 1):
        #             publicTime = self.r.parse('\d+-\d+-\d+ \d+:\d+:\d+' ,commentTime[index])[0]
        #             # 提取时间
        #             if URLStorage.storeupdatetime(params.originalurl, publicTime):
        #                 cmti = CommentInfo()
        #                 cmti.content = comments[index].text.replace('\r\n', '').strip()
        #                 commentsInfo.append(cmti)
        #
        #         # 保存获取的评论
        #         if len(commentsInfo) > 0:
        #             self.commentstorage.store(params.originalurl, commentsInfo)
        #     else:
        #         Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))
        # except Exception,e:
        #     traceback.print_exc()