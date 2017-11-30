# encoding=utf8

##############################################################################################
# @file：Kr36Comments.py
# @author：QW_Liang
# @date：2017/09/12
# @version：Ver0.0.0.100
# @note：36氪创业资讯页获取评论的文件
##############################################################################################

import json
import math
import re
import traceback
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
##############################################################################################
# @class：Kr36Comments
# @author：QW_Liang
# @date：2017/09/12
# @version：Ver0.0.0.100
# @note：36氪创业资讯页获取评论的文件
##############################################################################################
class Kr36Comments(SiteComments):
    COMMENT_URL = 'http://36kr.com/api/comment?cid={0}&ctype=post&per_page={1}&page={2}'
    STEP_1 = None
    STEP_2 = '2'
    STEP_3 = '3'

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/09/12
    # @note：Kr36Comments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 30

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/12
    # @note：Kr36Comments，通过Step1设置url，得到评论的总数，并根据评论总数得到获取其他评论的url。
    ##############################################################################################
    def process(self, params):
        try:
            if params.step is Kr36Comments.STEP_1:
                self.step1(params)
            elif params.step == Kr36Comments.STEP_2:
                self.step2(params)
            elif params.step == Kr36Comments.STEP_3:
                self.step3(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step=params.step))
                return
        except Exception,e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/12
    # @note：根据主页获取评论ID，传入评论页，获取评论
    ##############################################################################################
    def step1(self, params):
        try:
            Logger.getlogging().info("Kr36Comments.STEP_1")
            cid = self.r.parse('^http://36kr.com/p/(\d+)\.html', params.originalurl)[0]
            content = params.content

            page_content = content.split('<script>var props={"detailArticle|post":')[1].split(',"abTest|abtest":')[0]

            dump_content = eval(json.dumps(page_content))
            json_content = json.loads(dump_content)
            info_title = json_content["title"]
            info_content = json_content["content"]
            info_pubtime = TimeUtility.getformattime(json_content["published_at"])
            info_clicknum = json_content["counters"]["view_count"]
            info_cmtnum = json_content["counters"]["comment"]
            info_fansnum = json_content["counters"]["favorite"]
            info_votenum = json_content["counters"]["like"]
            # 去除HTML标签
            info_content = re.compile('</?\w+[^>]*>').sub('',info_content)
            if info_title:
                title = info_title
                # NewsStorage.settitle(params.originalurl,info_title)
            if info_content:
                body = info_content
                # NewsStorage.setbody(params.originalurl,info_content)
            if info_clicknum:
                clicknum = info_clicknum
                # NewsStorage.setclicknum(params.originalurl, info_clicknum)
            if info_pubtime:
                publishdate = info_pubtime
                # NewsStorage.setpublishdate(params.originalurl, info_pubtime)
            if info_cmtnum:
                cmtnum = info_cmtnum
                # NewsStorage.setcmtnum(params.originalurl, info_cmtnum)
            if info_fansnum:
                fansnum = info_fansnum
                # NewsStorage.setfansnum(params.originalurl, info_fansnum)
            if info_votenum:
                votenum = info_votenum
                # NewsStorage.setvotenum(params.originalurl, info_votenum)
            data = {"title": title, "clicknum": clicknum, "votenum": votenum, "fansnum": fansnum,
                    "publishdate": publishdate,"body":body,"cmtnum":cmtnum}
            NewsStorage.seturlinfo(params.originalurl,"","" ,data)

            # 根据输入原始url, 拼出评论首页
            commentinfo_url = Kr36Comments.COMMENT_URL.format(cid, self.page_size, 1)
            self.storeurl(commentinfo_url, params.originalurl, Kr36Comments.STEP_2,{'cid':cid})
        except:
            Logger.printexception()
    ##############################################################################################
    # @functions：step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/12
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def step2(self, params):
        try:
            Logger.getlogging().info("Kr36Comments.STEP_2")
            # 将STEP_1中的cid传下来
            cid = params.customized['cid']

            jsoncontent = json.loads(params.content)
            comments_count = jsoncontent['data']['total_items']
            page_count = jsoncontent['data']['total_pages']
            # 判断增量
            cmtnum = CMTStorage.getcount(params.originalurl)
            if cmtnum >= comments_count:
                return

            #最多只取十页评论
            # page_num = int(math.ceil(float(comments_count - cmtnum) / self.page_size))
            if page_count >= self.maxpages:
                page_count = self.maxpages
            lasttime = CMTStorage.getlastpublish(params.originalurl,True)

            for page in range(1, page_count+1, 1):
                commentinfo_url = Kr36Comments.COMMENT_URL.format(cid, self.page_size, page)
                self.storeurl(commentinfo_url, params.originalurl, Kr36Comments.STEP_3,lasttime)
        except:
            Logger.printexception()

    ##############################################################################################
    # @functions：step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：QW_Liang
    # @date：2017/09/12
    # @note：根据输入的html(json文件），得到评论
    ##############################################################################################
    def step3(self, params):
        try:
            Logger.getlogging().info("Kr36Comments.STEP_3")
            # Step3: 通过Step2设置的url，得到所有评论，抽取评论
            jsoncontent = json.loads(params.content)
            lasttime = params.customized
            for index in range(0, len(jsoncontent['data']['items']), 1):
                # 提取评论内容
                content = jsoncontent['data']['items'][index]['content']
                # 提取时间
                publicTime = jsoncontent['data']['items'][index]['created_at']
                curtime = TimeUtility.getuniformtime(TimeUtility.getuniformtime(publicTime, u'%Y-%m-%d %H:%M:%S'))
                nick = jsoncontent['data']['items'][index]['user']['name']

                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()