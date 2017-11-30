# coding=utf-8

##############################################################################################
# @file：zonghengBbsComments.py
# @author：Ninghz
# @date：2016/12/06
# @version：Ver0.0.0.100
# @note：纵横论坛获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/02/08
# @note:第121行添加了对pubtime时间的转换
###############################################################################################
import re
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime
# from utility.bbscommon import BBSCommon
from bs4 import BeautifulSoup

##############################################################################################
# @class：BbsComments
# @author：ninghz
# @date：2016/12/06
# @note：纵横论坛获取评论的类，继承于SiteComments类
##############################################################################################
class BbsComments(SiteComments):
    # 分支条件
    STEP_2 = '2_bbs'
    STEP_3 = '3_bbs'
    BBS_URL = 'http://bbs\.zongheng\.com/viewthread\.php\?.*&page=(\d+)'
    PAGE_SIZE = 20

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Ninghz
    # @date：2016/12/06
    # @note：BookComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：getcomments_step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/06
    # @note：根据输入url，拼出获取评论总数的url
    ##############################################################################################
    def getcomments_step1(self, params):
        domainUrl = params.originalurl
        if params.originalurl.find('&page=') > -1:
            domainUrl = params.originalurl[0:params.originalurl.index('&page=')]
        self.storeurl(params.originalurl, params.originalurl, BbsComments.STEP_2, {'domainUrl': domainUrl})

    ##############################################################################################
    # @functions：getcomments_step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/6
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ##############################################################################################
    def getcomments_step2(self, params):
        domainUrl = params.customized['domainUrl']
        # 获取总页数
        # lastpg = BBSCommon.gettotalpages(params.content, '//*[@class="pages"]/a')
        lastpgtemp = XPathUtility(params.content).getlist('//*[@class="pages"]/a')
        listtemp = []
        for temp in lastpgtemp:
            listtemp.append(re.findall(r'(\w*[0-9]+)\w*', temp))
        lastpg = int(max(listtemp)[0])
        Logger.getlogging().debug(lastpg)
        params.customized['lastpg'] = lastpg
        # 获取当前评论页码
        if params.url.find('&page=') > -1:
            pg = self.r.parse(BbsComments.BBS_URL, params.url)[0]
        else:
            pg = '1'
            params.url = domainUrl + '&page=1'
        # 获取当前页面评论
        self.getComments(params, BbsComments.BBS_URL)
        # 判断页数
        if lastpg >= self.maxpages:
            lastpg = self.maxpages

        cmtnum = CMTStorage.getcount(params.originalurl, True)
        start = int(cmtnum / self.PAGE_SIZE) + 1
        end = int(lastpg)
        if end > start + self.maxpages:
            start = end - self.maxpages

        for page in range(end, start - 1, -1):
            # 当前页面不再传递给第三步
            if page == int(pg):
                continue
            commentUrl = domainUrl + '&page=' + str(page)
            Logger.getlogging().debug(commentUrl)
            self.storeurl(commentUrl, params.originalurl, BbsComments.STEP_3, {'domainUrl': domainUrl, 'lastpg': lastpg})

    ##############################################################################################
    # @functions：getcomments_step3
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Ninghz
    # @date：2016/12/06
    # @note：根据输入html，得到评论
    ##############################################################################################
    def getcomments_step3(self, params):
        self.getComments(params, BbsComments.BBS_URL)


    def getComments(self, params, url):
        # 当前评论页码
        pg = self.r.parse(url, params.url)[0]
        soup = BeautifulSoup(params.content, 'html5lib')
        # 帖子内容
        infos = soup.select('tr > td.postcontent')
        # 发表时间，内容格式[发表于 2016-10-7 18:04:25]
        comments = []
        # 第一页的第一条内容为正文
        if pg == '1':
            start = 1
        else:
            start = 0
        for info in infos[start:]:
            # 取主评论
            if info.select_one('div[class="postmessage defaultpost"]'):
                content = info.select_one('div[class="postmessage defaultpost"]').get_text()\
                    .replace('\t','').replace('\n','').replace(' ','').strip()
                updatetime = info.select_one('div.postinfo > font').get_text().strip()[4:] + ':00'
                curtime = getuniformtime(updatetime)
                nick = 'none'
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        comments_couts = CMTStorage.getcount(params.originalurl)
        NewsStorage.setcmtnum(params.originalurl, comments_couts)
