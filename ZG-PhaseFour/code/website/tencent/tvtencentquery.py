# -*- coding: utf-8 -*-
################################################################################################################
# @file: tencentquery.py
# @author: JiangSiwei
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################

from utility.common import Common
from website.common.s2query import SiteS2Query
import re
from log.spiderlog import Logger
import traceback
from bs4 import BeautifulSoup
from configuration.constant import SPIDER_S2_WEBSITE_VIDEO

################################################################################################################
# @class：tencentquery
# @author：JiangSiwei
# @date：2016/11/22
# @note：
################################################################################################################
class TvtencentQuery(SiteS2Query):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SohuS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self,parent=None):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'http://v.qq.com/'
        self.ORIGINAL_QUERY_TEMPLATE = 'https://v.qq.com/x/search/?q={key}'
        self.QUERY_TEMPLATE = 'https://v.qq.com/x/search/?ses={session}&q={key}&filter={ufilter}&cur={page_size}'
        self.AC_QUERY_TEMPLATE = 'http://ac.qq.com/Comic/searchList/search/{key}/page/{page_size}'
        self.QUERY_TEMPLATE_FILTER='sort={0}&pubfilter={1}&duration={2}&tabid={3}'
        self.DEFAULT_PAGE_SIZE = 28
        
        #searchid表示时间，一周内时设置为9，orderby表示最新回复时间，kw表示搜索关键字，page表示页面
        #self.BOOK_QUERY_TEMPLATE = 'http://bbs.book.qq.com/search.php?mod=forum&searchid={searchid}&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw={key}&p={page}'
    
        self.TV_FIRST = 'TV_FIRST'
        self.TV_SECOND = 'TV_SECOND'
        self.TV_EACH = 'TV_EACH'
        if parent:
            self.website = parent.website             
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query
    ################################################################################################################
    def query(self, info):
        q = Common.urlenc(info)
        urls1 = [self.ORIGINAL_QUERY_TEMPLATE.format(key = q)]
        self.__storeqeuryurllist__(urls1, self.TV_FIRST, {'key':q})
        
    
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################    
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        if params.step == self.TV_FIRST:
            self.step1(params)
        if params.step == self.TV_SECOND:
            self.step2(params)
        if params.step == self.TV_EACH:
            self.step3(params)  
   
          
    ################################################################################################################
    # @functions：step1
    # @params： params
    # @return：none
    # @note：获取ses关键字，来源于session
    ################################################################################################################         
    #----------------------------------------------------------------------
    def step1(self,params):
        """获取ses关键字"""
        key = params.customized['key']
        session = re.findall("session:\s\'(.+?)\'",params.content)
        if session:
            session = session[0]   #截取后的数据是转换成url格式数据
        ufilter = Common.urlenc(self.QUERY_TEMPLATE_FILTER.format(1,2,0,0))
        #测试专用(0,0,0,0)
        #ufilter = Common.urlenc(self.QUERY_TEMPLATE_FILTER.format(0,0,0,0))
        urls = [self.QUERY_TEMPLATE.format(session=session,key=key,ufilter=ufilter,page_size=1)]
        self.__storeqeuryurllist__(urls, self.TV_SECOND, {'session':session,'key':key,'ufilter':ufilter})
    ################################################################################################################
    # @functions：step2
    # @params： params
    # @return：none
    # @note：获取url列表（腾讯视频页面数获取失败）
    ################################################################################################################   
    #----------------------------------------------------------------------
    def step2(self,params):
        """获取页面"""
        session = params.customized['session']
        key = params.customized['key']
        ufilter = params.customized['ufilter']
        pages = re.findall('pages:\s(\d+?);',params.content)[0]
        #测试专用,最多只一页，所以
        #pages = 1
        urllist = []
        for page in range(1,int(pages)+1):
            url = self.QUERY_TEMPLATE.format(session=session,key=key,ufilter=ufilter,page_size=page)
            urllist.append(url)
        self.__storeqeuryurllist__(urllist,self.TV_EACH,{'key':key})           
        
    
    ################################################################################################################
    # @functions：step3
    # @params： params
    # @return：none
    # @note：解析每一页面，获取链接
    ################################################################################################################   
    #----------------------------------------------------------------------
    def  step3(self,params):
        """解析每一页面"""
        try:
            key = Common.urldec(params.customized['key'])
            soup = BeautifulSoup(params.content,'html.parser')
            urllist = []
            #1.判断是合集还是单集
            #2.判断是电视剧、综艺、电影
            #<span class="type">电视剧\综艺\电影<span>
            #3.判断跟新数量
            #合集，电视剧class="result_episode_list cf"或综艺class="result_link_list cf"[纯综艺和电视剧综艺]
            items_v = soup.find_all(attrs={'class':re.compile('result_item_v')})
            if items_v:  
                for item in items_v:
                    flag = None
                    title = item.select_one('h2.result_title > a')
                    # if key not in title.get_text():
                    if not Common.checktitle(key, title.get_text()):
                        continue
                    #判断是否是电视剧,flag = 'tv',需要reversed序列，按从大到小排序,在剔除预告片
                    videoObj = None
                    tvObj = item.select_one('.result_episode_list')  
                    if tvObj:
                        flag = 'tv'
                        videoObj = tvObj
                    #判断是否是综艺,flag = 'vv'    'variaty vedio'   
                    vvObj = item.select_one('.result_link_list')
                    if vvObj:
                        flag = 'vv'
                        videoObj = vvObj
                    #针对flag='tv',flag='vv'        
                    if videoObj:
                        #正确的url序列
                        tvs = videoObj.select('div.item > a')
                        if flag == 'tv':
                            tvs = reversed(tvs)
                        tvs = [tv for tv in  tvs if re.findall('^http[s]{0,1}://',tv.get('href'))]   
                        
                        #计数'预告'个数
                        imgmarkObjs = videoObj.select('.item > .mark_v > img')
                        altlen = 0
                        if imgmarkObjs:
                            for i in range(len(imgmarkObjs)):
                                alt = imgmarkObjs[i].get('alt')
                                if re.search('预告',alt) or re.search(u'预告',alt):
                                    altlen += 1
                        #剔除预告片
                        urlitems = tvs[altlen:altlen+3]
                        for urlitem in urlitems:
                            #print 'uuuuuuuuuuuuuuuuuuuu:',urlitem.get('href')
                            url = urlitem.get('href')
                            if re.search('http://v.qq.com/x/page/\w+\.html',url):
                                #url = url.replace('page','cover/lvxqk7s7yynbdba')
                                url = url.replace('http://','https://')
                            urllist.append(url)
                        continue
                            
                    #如果以上都不是，(可以继续判断是否是电影,flag = 'mv'    预告与花絮不抓取，只抓取主链接)
                    otherObj = item.select_one('h2.result_title > a')
                    if otherObj:
                        if re.search('电影',otherObj.get_text()) or re.search(u'电影',otherObj.get_text()):
                            flag = 'mv'
                        url = otherObj.get('href')
                        if re.search('http://v.qq.com/x/page/\w+\.html',url):
                            ##url = url.replace('page','cover/lvxqk7s7yynbdba')
                            url = url.replace('http://','https://')
                        urllist.append(url)       
                        continue
                       
                
            #单集
            items_h = soup.find_all(attrs={'class':re.compile('result_item_h')})
            if items_h:
                for item in items_h:
                    title = item.select_one('h2.result_title > a')
                    # if key not in title.get_text():
                    if not Common.checktitle(key, title.get_text()):
                        continue
                    url = item.select_one('h2.result_title > a').get('href')
                    if re.search('^http[s]{0,1}://',url):
                        if re.search('http://v.qq.com/x/page/\w+\.html',url):
                            url = url.replace('http://','https://')
                        urllist.append(url)
            #系列
            items_series = soup.find_all(attrs={'class':re.compile('result_series')})
            if items_series:
                for item in items_series:
                    title = item.select_one('.figure_title > a')
                    # if key not in title.get_text():
                    if not Common.checktitle(key, title.get_text()):
                        continue     
                    urlitems = item.select('.list_item > a')
                    for urlitem in urlitems:
                        url = urlitem.get('href')
                        if re.search('http://v.qq.com/x/page/\w+\.html',url):
                            #url = url.replace('page','cover/lvxqk7s7yynbdba')
                            url = url.replace('http://','https://')
                        urllist.append(url)
            if len(urllist) > 0:
                self.__storeurllist__(urllist,SPIDER_S2_WEBSITE_VIDEO) 
        except:
            Logger.printexception()
        
