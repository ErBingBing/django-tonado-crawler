# coding=utf-8

##############################################################################################
# @file：baidutiebacomments.py
# @author：Hedian
# @date：2016/12/02
# @version：Ver0.0.0.100
# @note：百度贴吧获取评论的文件
# @modify
# @author:Jiangsiwei
# @date:2017/2/13
# @note:第147-148行添加了贴吧页面过多时的限制
##############################################################r################################
import re
import math
import json
import time
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.gettimeutil import getuniformtime,compareNow
from bs4 import BeautifulSoup
from configuration import constant
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
##############################################################################################
# @class：BaiduTiebaComments
# @author：Hedian
# @date：2016/12/02
# @note：百度贴吧获取评论的类，继承于SiteComments类
##############################################################################################
class BaiduTiebaComments(SiteComments):
    BBS_URL_REG = '^http://tieba\.baidu\.com/\w+/\d+\?pid=\d+&cid=\d+#\d+'
    # 百度贴吧分支条件
    BAIDU_STEP1 = None
    BAIDU_TIEBA_FIRST_PAGE = 'BAIDU_TIEBA_FIRST_PAGE'
    BAIDU_TIEBA_EACH_PAGE = 'BAIDU_TIEBA_EACH_PAGE'
    BAIDU_TIEBA_HUIFU_PAGE = 'BAIDU_TIEBA_HUIFU_PAGE'
    PAGE_SIZE = 10
    BBS_TITLE = ''
    COMMENT_URL = 'https://tieba.baidu.com/p/{tid}?pn={page}'
    REPLY_URL = 'https://tieba.baidu.com/p/totalComment?tid={tid}&fid={fid}&pn={pn}&see_lz=0'
    REPLY_JSONDATA = {}
    #帖子超过7天后就不取了
    COMMENT_LIMIT_DAYS = 7
    ##############################################################################################
    # @functions：__init__
    # @return：None
    # @author：Hedian
    # @date：2016/12/02
    # @note：BaiduTiebaComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent=None):
        SiteComments.__init__(self)
        if parent:
            self.website = parent.website
    
    def process(self, params):
        # 1. 根据输入原始url, 获得子域名
        field = self.r.parse('^http[s]{0,1}://(\w+)\.baidu\.com.*', params.originalurl)[0]
        if not field == 'tieba':
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
            return 
        if params.step is BaiduTiebaComments.BAIDU_STEP1:
            self.getcomments_step1(params)
        elif params.step == BaiduTiebaComments.BAIDU_TIEBA_EACH_PAGE:
            self.getpagecomments_step2(params)
        elif params.step == BaiduTiebaComments.BAIDU_TIEBA_HUIFU_PAGE:
            self.get_comment_reply_step3(params) 
            
    ##############################################################################################
    # @functions：getcomments_step1
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/12/02
    # @note：根据输入url，拼出获取评论总页面url
    ##############################################################################################
    def getcomments_step1(self, params):
        try:
            tid = re.findall('/p/(\d+)',params.originalurl)
            if tid:
                tid = tid[0]
            else:
                return 
            fid = self.r.getid('forum_id',params.content)

            soup = BeautifulSoup(params.content, "html5lib")
            body = soup.find(attrs={'id':re.compile('post_content')})
            
            if body:
                NewsStorage.setbody(params.originalurl, body.get_text())
            else:
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)    
            count = soup.select('.l_posts_num > .l_reply_num > span')
            if count:
                comment_count = count[0].get_text()
                page_num = count[1].get_text()
            else:
                comment_count = 0
                page_num = 1
        
            if int(page_num) > self.maxpages:
                page_num = self.maxpages        
            # 拼接获取uniqid的url
            for page in range(1,int(page_num)+1):
                flag = True
                if page == 1:
                    params.customized['page'] = 1
                    flag = self.getpagecomments_step2(params)
                if fid:
                    if not flag:
                        break
                    reply_url = BaiduTiebaComments.REPLY_URL.format(tid=tid, fid=fid, pn=page)  
                    self.storeurl(reply_url, params.originalurl, BaiduTiebaComments.BAIDU_TIEBA_HUIFU_PAGE)
                if page == 1:
                    continue
                comment_url = BaiduTiebaComments.COMMENT_URL.format(tid=tid,page=page)
                self.storeurl(comment_url, params.originalurl, BaiduTiebaComments.BAIDU_TIEBA_EACH_PAGE,{'page':page})
        except:
            Logger.printexception()
    ##############################################################################################
    # @functions：getpagecomments
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @page：获取的当前页数
    # @return：无
    # @author：Hedian
    # @date：2016/12/05
    # @note：根据输入的html，得到评论
    ##############################################################################################
    def getpagecomments_step2(self, params):
        try:
            page = params.customized['page']
            soup = BeautifulSoup(params.content, "html5lib")
            d_post_content_main = soup.select('#j_p_postlist > div.j_l_post')
            if page == 1:
                main_item = d_post_content_main[0]
                #print main_item
                pubtimes = ''
                pubtimesobj = main_item.select('.tail-info')
                if pubtimesobj:
                    pubtimes = getuniformtime(pubtimesobj[-1].get_text().strip())            
                else:
                    pubtimeslist = re.findall('\d+-\d+-\d+ \d+:\d+',str(main_item))
                    if pubtimeslist:
                        pubtimes = getuniformtime(pubtimeslist[0])
                if pubtimes:
                    NewsStorage.setpublishdate(params.originalurl, pubtimes)
                    if not compareNow(pubtimes,self.COMMENT_LIMIT_DAYS):
                        Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NOMATCHTIME)
                        #超过7天的帖子，不在取回复/评论了
                        return False
                d_post_content_main = d_post_content_main[1:]
            comments = []
            for item in d_post_content_main:
                try:
                    comment = item.find(attrs={'id': re.compile("post_content")})
                    if not comment:
                        continue
                    content = comment.get_text().strip()
                    pubtimes = ''
                    pubtimesobj = item.select('.tail-info')
                    if pubtimesobj:
                        pubtimes = getuniformtime(pubtimesobj[-1].get_text().strip())            
                    else:
                        pubtimeslist = re.findall('\d+-\d+-\d+ \d+:\d+',str(item))
                        if pubtimeslist:
                            pubtimes = getuniformtime(pubtimeslist[0])
                    if not pubtimes:
                        if not CMTStorage.exist(params.originalurl, content, TimeUtility.getdatebefore(0), 'nick'):
                            CMTStorage.storecmt(params.originalurl, content, TimeUtility.getdatebefore(0), 'nick')                         
                        continue
                    #判断评论是否是前一天的
                    Logger.getlogging().debug(pubtimes)
                    if self.isyestoday(pubtimes):
                        if not CMTStorage.exist(params.originalurl, content, pubtimes, 'nick'):
                            CMTStorage.storecmt(params.originalurl, content, pubtimes, 'nick')               
                except:
                    Logger.printexception()
            return True
        except:
            Logger.printexception()
            return False
    #----------------------------------------------------------------------
    def  get_comment_reply_step3(self,params):
        """"""
        try:
            jsondata = json.loads(params.content)
            data = jsondata['data']
            if data:
                comment_list = data['comment_list']
                for comment_id in comment_list:
                    try:
                        comments = comment_list[comment_id]
                        comment_list_num = comments['comment_list_num']
                        if int(comment_list_num) <= 0:
                            continue
                        for info in comments['comment_info']:
                            curtime = getuniformtime(str(info['now_time']))
                            content = info['content']
                            if not CMTStorage.exist(params.originalurl, content, curtime, 'nick'):
                                CMTStorage.storecmt(params.originalurl, content, curtime, 'nick')                                            
                    except:
                        Logger.printexception()
        except:
            Logger.printexception()
        
    #----------------------------------------------------------------------
    @staticmethod
    def filters(s):
        left = 0
        right = 0
        s1 = '<'
        s2 = '>'
        while True:
            if s1 not in s or s2 not in s:
                break            
            if s1 in s: 
                left = s.index(s1)
            if s2 in s:
                right = s.index(s2)      
            if right:
                s = s.replace(s[left:right+1],'')
        return s
    
    @staticmethod
    def isyestoday(times):
        if isinstance(times,str):
            times = time.mktime(time.strptime(times, "%Y-%m-%d %H:%M:%S"))
        now = time.time() - time.timezone
        cha = 60*60*24*1
        midnight = now - (now % cha) + time.timezone
        premidnight =midnight- cha
        if int(times) >= premidnight and int(times) < midnight:
            return True
        return False