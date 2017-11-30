# encoding=utf-8

#################################################################################
# @class：CommenComments
# @author：JiangSiwei
# @date：2016/11/30
# @note：获取bbs评论的文件，继承于SiteComments类
#################################################################################
import json
import math
import re

from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from configuration import constant 

class CommenComments(SiteComments):
    
    __instance = None
    STEP_DEFAULT_VALUE = None
    STEP_COMMENT_EACH_PAGE = 'step_each'
    STEP_1_2 = 'step_1_2'
    patterns = ['^http://[(bbs)|(gz)|(moba)].*/\w+-\d+-\d+-\d.*','^http://[(www)|(xsbbs)|(bbs)|(moba)].*/forum\.php\?mod=\w+&tid=\d+']  
    '''
    目前为止，满足该url的正则表达式共有26个论坛网站
    http://bbs.book.qq.com/t-123575-1-1.html
    http://bbs.17k.com/thread-3334098-1-1.html
    http://bbs.dmzj.com/thread-1147358-1-1.html
    http://bbs.duowan.com/thread-45100542-1-1.html
    http://bbs.18183.com/thread-11410834-1-1.html
    http://bbs.laohu.com/thread-679115-1-1.html
    http://bbs.gamersky.com/thread-934840-1-1.html
    http://bbs.131.com/thread-3220343-1-1.html
    http://bbs.gao7.com/thread-2507086-1-1.html
    http://bbs.gametanzi.com/thread-22-1-1.html
    http://bbs.tgbus.com/thread-6287904-1-1.html
    http://bbs.52pk.com/thread-6587326-1-1.html
    http://bbs.appgame.com/thread-881740-1-1.html
    http://bbs.ptbus.com/thread-3286252-1-1.html
    http://bbs.shouyou.com/thread-81632-1-1.html
    http://bbs.angeeks.com/thread-3972178-1-1.html
    http://bbs.gfan.com/android-8388000-1-1.html
    http://bbs.17173.com/thread-9006964-1-1.html
    http://bbs.u17.com/forum.php?mod=viewthread&tid=327368
    http://bbs.78dm.net/forum.php?mod=viewthread&tid=474772
    http://bbs.narutom.com/forum.php?mod=viewthread&tid=220105
    http://bbs.zymk.cn/forum.php?mod=viewthread&tid=606934
    http://www.7acg.com/forum.php?mod=viewthread&tid=6669
    http://www.gxdmw.com/forum.php?mod=viewthread&tid=95709   ---> http://www.gxdmw.com/thread-82010-1-1.html
    http://xsbbs.zymk.cn/forum.php?mod=viewthread&tid=217595
    http://moba.uuu9.com/forum.php?mod=viewthread&tid=4407873
    '''
    
    def __init__(self, parent = None):
        SiteComments.__init__(self)
        self.page_size = 10
        self.page_size2 = 20
        self.page_size3 = 15
        self.COMMENTS_URL = 'http://{website}/{area}-{url_id}-{page}-1.html'        #'format(website=website,area=area,url_id=url_id,page=page)'
        self.FORUM_URL = 'http://{website}/forum.php?mod={area}&tid={url_id}&page={page}'
        self.cmt_page_numCSS = {'pageCss':'#pgt > .pgt > .pg > a','cmtnumCss':'.hm > .xi1'}
        self.cmt_page_numCSS2 = {'pageCss':'#nav_hd > .la_fy > .pg > a','cmtnumCss':'.hm > .xi1'}
        self.cmt_page_numCSS3 = {'pageCss':'#pgt > .pg > a','cmtnumCss':'.hm > .xi1'}
        self.cmt_page_numCSS4 = {'pageCss':'.pg > a','cmtnumCss':'.hm > .xi1'}
        self.commentCsskey={'subject_idkey':'thread_subject','table_idkey':'pid','time_idkey':'authorposton','content_idkey':'(postmessage)|(locked)','table_summarykey':'pid'}
        if parent is not None:
            self.website = parent.website
         
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url,抽出的评论和最新评论的创建时间
    #          
    # @author：JiangSiwei
    # @date：2016/11/28
    # @note：Step1：先通过originalurl获取到能获取comment_id的url,并传递给共通模块，通过获取html中得到comment_id及url_id 
    #        Step2：通过共通模块传入的html内容获取到评论总数及item,artId，拼出获取评论的url，并传递给共通模块
    #               通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则保存最新更新时间 
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则抓取新增的数据
    #               
    ##############################################################################################        
    #----------------------------------------------------------------------          
    def process(self, params):
        """
        """ 
        if params.step == self.STEP_DEFAULT_VALUE:
            self.step1(params)
        elif params.step == self.STEP_1_2:
            self.step1_2(params)
        elif params.step == self.STEP_COMMENT_EACH_PAGE:
            self.step2(params)
            
    ################################################################################################################
    # @functions：step1
    # @params： params
    # @return：none
    # @note：获取url_id,page_num关键字,拼出评论url列表
    ################################################################################################################       
    #----------------------------------------------------------------------
    def  step1(self,params):
        """"""
        #print params.content
        try:
            website = re.findall('http://(.*?)/',params.originalurl)[0] 
            # re.search('^http://[(bbs)|(gz)|(moba)].*/\w+-\d+-\d+-\d.*',params.originalurl):
            if re.search('^http://[(bbs)|(gz)|(moba)|(gxdmw)].*/\w+-\d+-\d+-\d.*',params.originalurl):
                area = re.findall('com/(\w+?)-',params.originalurl)[0]
                url_id = re.findall('\d+',params.originalurl)[-3]
            elif re.search('^http://[(www)|(xsbbs)|(bbs)|(moba)].*/forum\.php\?mod=\w+(&fid=\d+)?&tid=\d+',params.originalurl):
                area = re.findall('mod=(\w+?)&',params.originalurl)[0]
                url_id = re.findall('tid=(\d+)',params.originalurl)[0]  
            else:
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
                return                
            
            soup = BeautifulSoup(params.content,'html5lib')
            #主贴内容、时间、查看数、回复数，页面数

            main_content = soup.find(attrs={'id':re.compile(self.commentCsskey['content_idkey'])})
            if main_content:
                main_content = main_content.get_text()
                NewsStorage.setbody(params.originalurl, main_content)
            else:
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_XPATHVALUE)
                return
            curtimeobj = soup.find(attrs={'id':re.compile(self.commentCsskey['time_idkey'])})
            if curtimeobj:
                if curtimeobj.select_one('span'):
                    curtime = curtimeobj.select_one('span').get('title')
                else:
                    curtime = curtimeobj.get_text()
                NewsStorage.setpublishdate(params.originalurl, TimeUtility.getuniformtime(curtime))
            
            if re.search('^http://www\.gxdmw\.com/.*',params.originalurl):
                #只是针对http://www.gxdmw.com/网站
                cmtnum = soup.find(attrs={'class':"vwthdreplies y"})
                curcmtnum = cmtnum.select_one('strong').get_text()
            else:
                cmtnum = soup.select(self.cmt_page_numCSS['cmtnumCss'])
                cmt_read = cmtnum[0].get_text()
                curcmtnum = cmtnum[1].get_text()
            curcmtnum = int(curcmtnum)
            NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
            dbcmtnum = CMTStorage.getcount(params.originalurl, True)
            if dbcmtnum >= curcmtnum:
                return
            #直接取
            pageObj = soup.select(self.cmt_page_numCSS4['pageCss'])
            if pageObj:
                Logger.getlogging().debug('first get pageObj:%s'% pageObj[-2].get_text().strip('.'))
            if not pageObj:
                pageObj = soup.select(self.cmt_page_numCSS['pageCss'])
            if not pageObj:
                pageObj = soup.select(self.cmt_page_numCSS2['pageCss'])
            if not pageObj:
                pageObj = soup.select(self.cmt_page_numCSS3['pageCss'])
            if pageObj:
                page_num = pageObj[-2].get_text().strip('.')
            else:
                page_num = 1
                
            #此部分只能具体网站可做具体的页面数量限制
            if re.search('^http://bbs\.(17173|17k|gamersky)\.com/.*', params.originalurl):
                page_size = self.page_size2
            elif re.search('^http://bbs\.78dm\.net/.*', params.originalurl):
                page_size = self.page_size3
            else:
                page_size = self.page_size
            start = int(dbcmtnum / page_size) + 1
            end = int(page_num)
            if end > start+ self.maxpages:
                start =  end - self.maxpages
                
            params.customized['page'] = 1
            if end == 1:
                self.step2(params)
                return
            if start == 1:
                self.step2(params)
            #获取最后一页            
            if re.search('^http://[(bbs)|(gz)|(moba)|(gxdmw)].*/\w+-\d+-\d+-\d.*',params.originalurl):
                url = self.COMMENTS_URL.format(website=website,area=area,url_id=url_id,page=end)
            if re.search('^http://[(www)|(xsbbs)|(bbs)|(moba)].*/forum\.php\?mod=\w+(&fid=\d+)?&tid=\d+',params.originalurl):
                url = self.FORUM_URL.format(website=website,area=area,url_id=url_id,page=end)                
            if url:
                self.storeurl(url, params.originalurl, self.STEP_1_2,{'page':end, 'start':start, 'end':end, 
                                                                      'website':website, 'area':area, 'url_id':url_id})              
            #for page in range(end, start-1, -1):
                ##if int(page) == end:
                    ##params.customized['page'] = 1
                    ##if not self.step2(params):
                        ##break
                    ##continue
                #if re.search('^http://[(bbs)|(gz)|(moba)|(gxdmw)].*/\w+-\d+-\d+-\d.*',params.originalurl):
                    #url = self.COMMENTS_URL.format(website=website,area=area,url_id=url_id,page=page)
                #if re.search('^http://[(www)|(xsbbs)|(bbs)|(moba)].*/forum\.php\?mod=\w+(&fid=\d+)?&tid=\d+',params.originalurl):
                    #url = self.FORUM_URL.format(website=website,area=area,url_id=url_id,page=page)                
                #if url:
                    #self.storeurl(url, params.originalurl, self.STEP_COMMENT_EACH_PAGE,{'page':page})             
        except:
            Logger.printexception()
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)
  
    #----------------------------------------------------------------------
    def step1_2(self,params):
        #最后一页
        start = params.customized['start']
        end = params.customized['end']
        website = params.customized['website']
        area = params.customized['area']
        url_id = params.customized['url_id']
        for page in range(end, start-1, -1):
            if int(page) == end:
                if not self.step2(params):
                    break
                continue
            if int(page) == 1:
                continue
            if re.search('^http://[(bbs)|(gz)|(moba)|(gxdmw)].*/\w+-\d+-\d+-\d.*',params.originalurl):
                url = self.COMMENTS_URL.format(website=website,area=area,url_id=url_id,page=page)
            if re.search('^http://[(www)|(xsbbs)|(bbs)|(moba)].*/forum\.php\?mod=\w+(&fid=\d+)?&tid=\d+',params.originalurl):
                url = self.FORUM_URL.format(website=website,area=area,url_id=url_id,page=page)                
            if url:
                self.storeurl(url, params.originalurl, self.STEP_COMMENT_EACH_PAGE,{'page':page})        
        
    ################################################################################################################
    # @functions：step2
    # @params： params
    # @return：none
    # @note：获取评论
    ################################################################################################################
    #----------------------------------------------------------------------
    def  step2(self,params):
        try:
            page = params.customized['page']
            soup = BeautifulSoup(params.content,'html5lib')
            subject = soup.find(attrs={'id':re.compile(self.commentCsskey['subject_idkey'])})
            if subject:
                subject = subject.get_text()
            else:
                pass
            tables = soup.find_all('table',attrs={'id':re.compile(self.commentCsskey['table_idkey']),'summary':re.compile(self.commentCsskey['table_summarykey'])})
        
            if page ==1:
                tables = tables[1:]

            if tables:
                #初始列表赋一个当前时间的值，避免后续报错
                publishlist = [TimeUtility.getcurrentdate(TimeUtility.DEFAULTFORMAT)]                   
                for table in tables:
                    try:
                        nick = table.select_one('.xw1').get_text()
                    except:
                        nick = 'anonymous'
                    try:
                        curtimeobj = table.find(attrs={'id':re.compile(self.commentCsskey['time_idkey'])})
                        if curtimeobj.select_one('span'):
                            curtime = curtimeobj.select_one('span').get('title')
                        else:
                            curtime = curtimeobj.get_text()
                    except:
                        curtime = TimeUtility.getuniformtime(0)
                    try:
                        content = table.find(attrs={'id':re.compile(self.commentCsskey['content_idkey'])}).get_text()
                    except:
                        content = ''
                    publishlist.append(curtime)
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                if not self.isnewesttime(params.originalurl, min(publishlist)):
                    return False         
            else:
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return True
        except:
            Logger.printexception()
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_SITE)


    @staticmethod
    def getinstance(parent=None):
        if CommenComments.__instance is None:
            if parent:
                CommenComments.__instance = CommenComments(parent)
            else:
                CommenComments.__instance = CommenComments()
        return CommenComments.__instance 