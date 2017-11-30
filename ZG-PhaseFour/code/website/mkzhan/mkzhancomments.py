# encoding=utf-8
##############################################################################################
# @file：mkzhancomments.py
# @author：Yangming
# @date：2016/12/12
# @version：Ver0.0.0.100
# @note：漫客栈获取评论的文件
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################
import time
import re
import json
import math
from storage.newsstorage import NewsStorage
from website.common.comments import SiteComments
from log.spiderlog import Logger
import traceback
from utility.xpathutil import XPathUtility
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import TimeUtility

##############################################################################################
# @class：MkzhanComments
# @author：Liyanrui
# @date：2016/11/18
# @note：漫客栈获取评论的类，继承于SiteComments类
##############################################################################################
class MkzhanComments(SiteComments):
    # https://www.mkzhan.com/comic/comment_list?comic_id=179552&page_num=1&page_size=100
    # COMMENTS_URL = 'http://www.mkzhan.com/index.php/comment/clist/?type=%s&aboutid=%s&page=%d'
    COMMENTS_URL = 'https://www.mkzhan.com/comic/comment_list?comic_id=%d&page_num=%d&page_size=%d'
    PAGE_SIZE = 100
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yangming
    # @date：2016/12/12
    # @note：漫客栈类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：Yangming
    # @date：2016/12/12
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is MkzhanComments.STEP_1:
                self.step1(params)
            elif params.step == MkzhanComments.STEP_2:
                self.step2(params)
            elif params.step == MkzhanComments.STEP_3:
                self.step3(params)
            else:
                Logger.getlogging().error('params.step == {step}'.format(step=params.step))
                return
        except Exception, e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/12
    # @note：根据主页获取评论ID及评论地址
    ##############################################################################################
    def step1(self, params):
        Logger.getlogging().info("MkzhanComments.STEP_1")
        # # 取得html中的commentType
        # comment_type = self.r.getid('commentType', params.content)
        #
        # # 取得html中的aboutid
        # aboutid = self.r.getid('aboutid', params.content)
        # if not comment_type  or not aboutid:
        #     Logger.getlogging().warning('{url}:40000 No commentType or No aboutid'.format(url=params.originalurl))
        #     return
        if NewsStorage.getclicknum(params.originalurl) <= 0:
            if self.r.search('<span>人气:\s<b>(.*?)<\/b>', params.content):
                clicknum = self.r.parse('<span>人气:\s<b>(.*?)<\/b>', params.content)[0]
                NewsStorage.setclicknum(params.originalurl, clicknum)

                # 获取comic_id
        comic_id = int(self.r.parse(r'^http[s]?://www\.mkzhan\.com/(\d+)/.*', params.originalurl)[0])
        if not comic_id:
            return
        # 取得评论url
        comments_url = MkzhanComments.COMMENTS_URL % (comic_id, 1, self.PAGE_SIZE)
        self.storeurl(comments_url, params.originalurl, MkzhanComments.STEP_2,
                      {'comic_id': comic_id})

    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/9
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        Logger.getlogging().info("MkzhanComments.STEP_2")
        comic_id = params.customized['comic_id']
        # aboutid = params.customized['aboutid']
        comments =  json.loads(params.content)
        comments_count = int(comments['data']['count'])
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        # 获取第一页的内容
        for it in comments['data']['list']:
            content = it['content']
            curtime = TimeUtility.getuniformtime(it['create_time'])
            nick = it['username']
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        # 设置cmtnum
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        if cmtnum >= comments_count:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages
        for page in range(2, page_num + 1, 1):
            comments_url = MkzhanComments.COMMENTS_URL % (comic_id, page, self.PAGE_SIZE)
            self.storeurl(comments_url, params.originalurl, MkzhanComments.STEP_3)

        # # 取得评论个数
        # comments_count = float(
        #     self.r.parse('\("\.pinglun_totle_num"\)\.html\("(.*)"\)', params.content).__getitem__(0))
        # if comments_count:
        #     NewsStorage.setcmtnum(params.originalurl, comments_count)
        # # 判断增量
        # cmtnum = CMTStorage.getcount(params.originalurl, True)
        # if cmtnum >= comments_count:
        #     return
        # page_count = 1
        # xparser = XPathUtility(params.content)
        # page_list = xparser.getcomments("//div[@class='pl_page']/a")
        # for index in range(len(page_list) - 1, 0, -1):
        #     list_item = page_list[index]
        #     if type(list_item) == str and list_item.isdigit():
        #         page_count = int(list_item)
        #         break
        # # 循环取得评论的url
        # for page in range(1, page_count + 1, 1):
        #     # 取得评论的url
        #     url = MkzhanComments.COMMENTS_URL % (comment_type, aboutid, page)
        #     self.storeurl(url, params.originalurl, MkzhanComments.STEP_3)

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Yangming
    # @date：2016/12/2
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        Logger.getlogging().info("MkzhanComments.STEP_3")
        comments = json.loads(params.content)
        for it in comments['data']['list']:
            content = it['content']
            curtime = TimeUtility.getuniformtime(it['create_time'])
            nick = it['username']
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        # comments = []
        # xparser = XPathUtility(params.content)
        # comment_infos = xparser.xpath("//html/body/div/div[2]/div[2]")
        # comment_times = xparser.getcomments("//div[@class='user_name_big']/span[2]")
        # year = time.strftime('%Y', time.localtime(time.time()))
        # for index in range(0, len(comment_infos)):
        #     # 网站上的评论时间只有月日，没有年，所以将年都设置成当前年份
        #     tm = getuniformtime(comment_times[index])
        #     if URLStorage.storeupdatetime(params.originalurl, tm):
        #         cmti = CommentInfo()
        #         comment_text = comment_infos[index].text
        #         if comment_text is None:
        #             comment_text = ""
        #         cmti.content = comment_text
        #         comments.append(cmti)

        # 保存获取的评论
        # if len(comments) > 0:
        #     self.commentstorage.store(params.originalurl, comments)