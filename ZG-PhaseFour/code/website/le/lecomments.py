# coding=utf-8
##############################################################################################
# @file：LetvComments.py
# @author：Liyanrui
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：乐视获取评论的文件
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
###############################################################################################
import json
import math
import re
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility
from utility.xpathutil import XPathUtility
from bs4 import BeautifulSoup
from website.common.changyanComments import ChangyanComments

##############################################################################################
# @class：LeComments
# @author：Liyanrui
# @date：2016/11/20
# @note：乐视获取评论的类，继承于SiteComments类
##############################################################################################
class LeComments(SiteComments):
    COMMENTS_URL = 'http://api.my.le.com/vcm/api/list?cid=%s&type=video&rows=20&page=%d&source=1&listType=1&xid=%s&pid=%s'
    COMMENTS_URL_TV = 'http://api.my.le.com/vcm/api/list?type=video&rows=20&page=%d&pid=%s'
    COMMENTS_URL_ZONGYI1 = 'http://api.my.le.com/vcm/api/list?type=video&rows=20&page=%d&pid=%s'
    COMMENTS_URL_ZONGYI2 = 'http://bbs.le.com/thread-%s-%d.html'
    PALYCOUNT_URL = 'http://v.stat.letv.com/vplay/getIdsInfo?ids={vid}' #http://v.stat.letv.com/vplay/getIdsInfo?ids=29107838
    
    PAGE_SIZE = 20
    STEP_1 = None
    STEP_SPORT_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4
    STEP_5 = 5
    STEP_PALY = 6



    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Liyanrui
    # @date：2016/11/20
    # @note：乐视类的构造器，初始化内部变量
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
    # @date：2016/11/20
    # @note：Step1：通过共通模块传入的html内容获取到pid，cid,，xid, 拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    #        Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        if self.r.search('http://sports\.le\.com/.*',params.originalurl):
            ChangyanComments(self).process(params)
        else:
            self.process_ptv(params)
        if params.step == None:
            self.getclick(params)
        elif params.step == self.STEP_PALY:
            self.setclick(params)

    def process_ptv(self,params):
        try:
            if params.step == LeComments.STEP_1:
                self.setp_1(params)
            elif params.step == LeComments.STEP_2:
                self.setp_2(params)
            elif params.step == LeComments.STEP_3:
                self.setp_3(params)
            elif params.step == LeComments.STEP_4:
                self.getcomments(params)
        except:
            Logger.printexception()
            
    def setp_1(self,params):
        # 乐视-电视剧的特殊模式
        if re.match(r'^http://tv\.le\.com/.*', params.url):
            # 评论参数pid取得
            if not self.r.search('pid:" (\d+)",', params.content):
                return
            pid = self.r.parse('pid:" (\d+)",', params.content)[0]

            # 取得评论url
            comments_url = LeComments.COMMENTS_URL_TV % (3, pid)
            self.storeurl(comments_url, params.originalurl, LeComments.STEP_2, {'pid': pid})
        # music模式
        elif re.match(r'^http://music\.le\.com/.*', params.url):
            # 评论参数pid取得
            pid = self.r.parse('pid=(\d+)"', params.content)[0]

            # 取得评论url
            comments_url = LeComments.COMMENTS_URL_TV % (1, pid)
            self.storeurl(comments_url, params.originalurl, LeComments.STEP_2, {'pid': pid})
        # 综艺模式
        elif re.match(r'^http://zongyi\.le\.com/.*', params.url):
            # 评论div是Comment模式时
            if re.search('zt_comment Comment', params.content):
                # 获取pid
                pid = self.r.getid('pid')
                if pid == '':
                    return

                # 取得评论url
                comments_url = LeComments.COMMENTS_URL_ZONGYI1 % (1, pid)
                self.storeurl(comments_url, params.originalurl, LeComments.STEP_5, {'pid': pid})
        # 其他模式
        else:
            # 评论参数cid取得
            cid = self.r.getid('cid', params.content, split=':')  
            # 评论参数xid取得
            xid = self.r.getid('vid', params.content, split=':') 
            # 评论参数pid取得
            pid = self.r.getid('pid', params.content, split=':') 
            if cid == '' or xid == '' or pid == '':
                return
            # 取得评论url
            comments_url = LeComments.COMMENTS_URL % (cid, 1, xid, pid)
            self.storeurl(comments_url, params.originalurl, LeComments.STEP_3,
                          {'cid': cid, 'xid': xid, 'pid': pid})
    
    def setp_2(self,params):
        # 取得评论件数
        comments = json.loads(params.content)
        comments_count = float(comments['total'])
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        if int(comments_count) == 0:
            return
        # 判断是否有增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        # 取得评论参数
        pid = params.customized['pid']

        # 综艺模式取得评论url
        if re.match(r'^http://zongyi\.le\.com/.*', params.url):
            for page in range(1, page_num + 1, 1):
                if page == 1:
                    self.geturlcomments(params)
                    continue
                url = LeComments.COMMENTS_URL_ZONGYI1 % (page, pid)
                self.storeurl(url, params.originalurl, LeComments.STEP_4)
        else:
            for page in range(1, page_num + 1, 1):
                if page == 1:
                    self.geturlcomments(params)
                    continue
                url = LeComments.COMMENTS_URL_TV % (page, pid)
                self.storeurl(url, params.originalurl, LeComments.STEP_4)

    def setp_3(self,params):
        # 取得评论件数
        comments = json.loads(params.content)
        comments_count = float(comments['total'])
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        if int(comments_count) == 0:
            return
        # 判断是否有增量
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PAGE_SIZE))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        # 取得评论参数
        cid = params.customized['cid']
        xid = params.customized['xid']
        pid = params.customized['pid']

        # 取得评论url列表
        for page in range(1, page_num + 1, 1):
            if page == 1:
                self.getcomments(params)
                continue
            url = LeComments.COMMENTS_URL % (cid, page, xid, pid)
            self.storeurl(url, params.originalurl, LeComments.STEP_4)
            
        
    def getcomments(self,params):
        comments = json.loads(params.content)
        # 获取评论
        for item in comments['data']:
            curtime = TimeUtility.getuniformtime(item['ctime'])
            content = item['content']
            nick = item['user']['username']
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)
                
    #----------------------------------------------------------------------
    def  getclick(self, params):
        pattern = 'https?://\w+\.le\.com.*/\w+/(\d+)\.html'
        if re.search(pattern, params.originalurl):
            if self.r.search(pattern, params.originalurl):
                vid = self.r.parse(pattern, params.originalurl)[0]
                playcount_url = self.PALYCOUNT_URL.format(vid=vid)
                self.storeurl(playcount_url, params.originalurl, LeComments.STEP_PALY)
        
        if NewsStorage.getpublishdate(params.originalurl) == TimeUtility.getintformtime(0):
            if self.r.search('https?://sports\.le\.com/video/\d+\.html', params.originalurl):
                #仅针对体育频道获取发布时间
                pubTime = XPathUtility(params.content).getstring('//*[@class="live-vedio-infor"]')
                publishdate = TimeUtility.getuniformtime(publishdate)
                NewsStorage.setpublishdate(params.originalurl, publishdate)    
            else:
                #仅针对综艺频道获取发布时间
                title = XPathUtility(params.content).getstring('//h1[@class="j-video-name video-name"]')
                if title:
                    if re.search('\d{8}', title):
                        publishdate = re.findall('\d{8}', title)[0]
                        NewsStorage.setpublishdate(params.originalurl, publishdate)                
    #----------------------------------------------------------------------
    def setclick(self,params):
        playcount = self.r.getid('play_count', params.content)
        votenum = self.r.getid('up', params.content)
        if playcount:
            NewsStorage.setclicknum(params.originalurl, playcount)
        if votenum:
            NewsStorage.setvotenum(params.originalurl, votenum)

         
      
        

