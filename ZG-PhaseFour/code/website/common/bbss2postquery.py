# -*- coding: utf-8 -*-
################################################################################################################
# @file: 
# @author: 
# @date:  
# @version: 
# @note:
################################################################################################################
import json
from lxml import etree
from configuration.constant import SPIDER_S2_WEBSITE_TIEBA
from utility.common import Common
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
from utility.regexutil import RegexUtility
from utility.httputil import HttpUtility
from bs4 import BeautifulSoup
import re
import urllib,urllib2
from  configuration import constant
from  utility.timeutility import TimeUtility
################################################################################################################
# @class：BBSS2PostQuery
# @author:
# @date：
# @note：初始化BBSS2PostQuery('http://bbs.dmzj.com/search.php?mod=forum')
################################################################################################################
class BBSS2PostQuery(SiteS2Query):
    post_urllist = ['http://bbs.appgame.com/search.php?mod=forum',
                    'http://bbs.shouyou.com/search.php?mod=forum',
                    'http://bbs.18183.com/search.php?mod=forum',
                    'http://bbs.gao7.com/search.php?mod=forum',
                    'http://bbs.17k.com/search.php?mod=forum',
                    'http://bbs.dmzj.com/search.php?mod=forum',

                    'http://bbs.17173.com/search.php?mod=forum',
                    'http://bbs.gamersky.com/search.php?mod=forum',
                    'http://bbs.131.com/search.php?mod=forum',
                    'http://bbs.gametanzi.com/search.php?mod=forum',
                    'http://www.7acg.com/search.php?mod=forum',
                    'http://www.gxdmw.com/search.php?mod=portal',
                    'http://bbs.zymk.cn/search.php?mod=forum',
                    'http://bbs.duowan.com/search.php?mod=forum',
                    'http://bbs.book.qq.com/search.php?mod=forum',
                    'http://bbs.78dm.net/search.php?mod=forum'
                    ]
    
    gbk_posturl = ['http://bbs.17173.com/search.php?mod=forum',
                   'http://bbs.appgame.com/search.php?mod=forum',
                   'http://bbs.shouyou.com/search.php?mod=forum',
                   'http://bbs.18183.com/search.php?mod=forum',
                   'http://bbs.131.com/search.php?mod=forum',
                   'http://bbs.gao7.com/search.php?mod=forum',
                   'http://bbs.gametanzi.com/search.php?mod=forum',
                   'http://bbs.duowan.com/search.php?mod=forum',
                   'http://bbs.book.qq.com/search.php?mod=forum',
                   'http://bbs.17k.com/search.php?mod=forum',
                   'http://bbs.dmzj.com/search.php?mod=forum'
                   ]   
    #POST_DATA = {'formhash': constant.SPIDER_POST_FORMHASH_VALUE, 'srchtxt':'','searchsubmit':'yes'}
    POST_DATA = {'srchtxt':'','searchsubmit':'yes'}
    QUERY_TEMP = '{post_url}&searchid={searchid}&orderby=lastpost&ascdesc=desc&searchsubmit=yes&page={page}'
    S2QUERY_FIRST_PAGE = 'POSTS2QUERY_FIRST_PAGE'
    S2QUERY_EACH_PAGE = 'POSTS2QUERY_EACH_PAGE'
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量,初始化传入post方法时的url
    ################################################################################################################
    def __init__(self,post_url,parent=None):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = post_url
        self.r = RegexUtility()
        #self.post_url = BBSS2PostQuery.POST_URL
        self.post_url = post_url
        self.queryinfo = ''
        if parent:
            self.website = parent.website
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch'
        }        
   
    #----------------------------------------------------------------------
    @staticmethod
    def isgbk_posturl(post_url):
        """判断该网页是否是gbk格式输入"""
        if post_url in BBSS2PostQuery.gbk_posturl:
            return True
        return False
        
    ################################################################################################################
    # @functions：pageprocess
    # @info： 对每一页获取的检索结果进行处理
    # @return：none
    # @note：需要标题命中,因为无法获取时间信息，所以不能按指定周期获得结果
    ################################################################################################################
    def query(self, info):
        if self.post_url not in BBSS2PostQuery.post_urllist:
            Logger.debug('{}:Not in tasking'.format(self.post_url))
            return
        if BBSS2PostQuery.isgbk_posturl(self.post_url):
            info = Common.trydecode(info)
            #info = info.decode('gbk').encode('utf-8')
        BBSS2PostQuery.POST_DATA['srchtxt'] =  info
        self.queryinfo = info
        self.__storeqeuryurl__(self.post_url, BBSS2PostQuery.S2QUERY_FIRST_PAGE, BBSS2PostQuery.POST_DATA,{'info':info})
    
    #----------------------------------------------------------------------
    def  step1(self,params):
        """"""
        info = params.customized['info']
        #print params.content
        #通过已经获取到首页url，通过get获取html内容后，解析获取S2的urllist
        soup = BeautifulSoup(params.content,'html5lib')
        #1.如果没有结果就直接退出
        if soup.find(attrs={"class":"emp xs2 xg2"}):
            Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NORESULTS)
            return
        if soup.select_one('.alert_btnleft'):
            Logger.log(params.originalurl, constant.ERRORCODE_WARNNING_NORESULTS)
            return        
        #2.如果有结果
           #2.1 只有一页时直接搜索第一页
           #2.2 如果有多页，需要先获取一个能拼出的说是有queryurllist的链接   
        if not soup.select_one('.pgs > .pg > label > span'):
            self.step2(params)
            return
        else:
            searchid = self.r.getid('searchid',params.content)
            pagetext = soup.select_one('.pgs > .pg > label > span').get_text()
            pagenum = re.findall('\d+',pagetext)[0]
            if int(pagenum) >= self.maxpages:
                pagenum = self.maxpages
            querylist = []
            for page in range(1,int(pagenum)+1):
                if int(page) == 1:
                    self.step2(params)
                    continue
                url = BBSS2PostQuery.QUERY_TEMP.format(post_url=self.post_url, searchid=searchid, page=page)
                querylist.append(url)
            self.__storeqeuryurllist__(querylist, BBSS2PostQuery.S2QUERY_EACH_PAGE, {'info':'info'})            
                                                 
    #----------------------------------------------------------------------
    def  step2(self,params):
        """解析每一搜索页面"""
        info = params.customized['info']
        soup = BeautifulSoup(params.content,'html5lib')
        divs = soup.select('.pbw')
        
        #divs = soup.select('h3.xs3 > a')
        if not divs:
            return
        urllist = []
        
        for div in divs:
            tm = div.select('p > span')[0].get_text()
            tm = TimeUtility.getuniformtime(tm)
            geturl = div.select_one('h3.xs3 > a').get('href')
            title = div.select_one('h3.xs3 > a').get_text()
            if not re.search('http://.*com.*',geturl):
                if re.search('(http://.*com).*',params.url):
                    urltemp = re.findall('(http://.*com).*',params.url)[0]
                elif re.search('(http://.*cn).*',params.url):
                    urltemp =re.findall('(http://.*cn).*',params.url)[0]
                elif re.search('(http://.*net).*',params.url):
                    urltemp =re.findall('(http://.*net).*',params.url)[0]                
                geturl = urltemp +'/'+ geturl
            if re.search('(http.*)&highlight',geturl):
                geturl = re.findall('(http.*)&highlight',geturl)[0]
    
            Logger.getlogging().info(Common.trydecode(title))
            #to compare time and match title
            if not TimeUtility.compareNow(tm, self.querylastdays):
                Logger.log(geturl, constant.ERRORCODE_WARNNING_NOMATCHTIME)
                continue
            if not Common.checktitle(Common.trydecode(info), Common.trydecode(title)):
                Logger.log(geturl, constant.ERRORCODE_WARNNING_NOMATCHTITLE)
                continue
            #print geturl
            urllist.append(geturl)
        self.__storeurllist__(urllist, SPIDER_S2_WEBSITE_TIEBA)
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        try:
            if params.step == BBSS2PostQuery.S2QUERY_FIRST_PAGE:
                self.step1(params)
            if params.step == BBSS2PostQuery.S2QUERY_EACH_PAGE:
                self.step2(params)  
        except:
            Logger.printexception()

    
    