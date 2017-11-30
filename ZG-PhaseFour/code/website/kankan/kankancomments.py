# encoding=utf-8

##############################################################################################
# @file：kankancomments.py
# @author：Yongjicao
# @date：2016/11/20
# @version：Ver0.0.0.100
# @note：迅雷看看视频获取评论的文件
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
##############################################################r################################

import json
import math
import datetime
import traceback
import time
import re
from lxml import etree

from utility.regexutil import RegexUtility
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
from bs4 import BeautifulSoup

##############################################################################################
# @class：KanKanComments
# @author：Yongjicao
# @date：2016/11/20
# @note：迅雷看看获取评论的类，继承于WebSite类
##############################################################################################
class KanKanComments(SiteComments):

    COMMENTS_URL1 = 'http://api.t.kankan.com/weibo_list_vod.json?movieid={movieid}&page={page}&perpage={perpage}'
    COMMENTS_URL2 = 'http://api.t.kankan.com/common_comment.json?type=%s&sid=%d&page=%d&perpage=%d'
    CLICK_URL = 'http://{type}.kankan.com/relation/{id1}/{id2}.json'
    TYPE1 = r'^http://vod\.kankan\.com/v/\d+/(\d+).shtml.*'
    TYPE2 = r'^http://(\w+)\.kankan\.com/\w+/\d+/(\d+).shtml.*'
    TYPE3 = r'^http://(\w+)\.kankan\.com/\w+/\w+/\d+/(\d+).shtml.*'
    STEP_1 = None
    STEP_2 = 2
    STEP_3 = 3
    STEP_CLICK = 'click'
    PERPAGE = 10

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：Yongjicao
    # @date：2016/11/20
    # @note：KanKanComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    # Step2：获取评论的所有url
    # Step3: 抽出的评论和最新评论的创建时间
    # @author：Yongjicao
    # @date：2016/11/20
    # @note：Step1：通过共通模块传入的html内容获取到movieid，拼出获取评论总数的url，并传递给共通模块
    # Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    # Step3：通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is KanKanComments.STEP_1:
                # 获取播放量（不是所有的视频都有播放量）
                self.setclicknum(params)
                if self.r.match(self.TYPE1,params.originalurl):
                    # Step1: 通过原始url得到moveid，得到获取评论的首页url。
                    movieid = self.r.parse(self.TYPE1, params.url)[0]
                    Logger.getlogging().debug(movieid)
                    commentinfo_url = KanKanComments.COMMENTS_URL1 .format (movieid = movieid,page=1,perpage = self.PERPAGE)
                    self.storeurl(commentinfo_url, params.originalurl, KanKanComments.STEP_2,{'movieid' : movieid})
                elif self.r.match(self.TYPE2,params.originalurl):
                    # Step1: 通过原始url得到type和sid,得到获取评论的首页url
                    self.substep1(params, self.TYPE2)
                elif self.r.match(self.TYPE3,params.originalurl):
                    # Step1: 通过原始url得到type和sid,vchannel得到获取评论的首页url
                    self.substep1(params, self.TYPE3)

            elif params.step == KanKanComments.STEP_2:
                self.step2(params)
            elif params.step == KanKanComments.STEP_3:
                self.step3(params)
            elif params.step == KanKanComments.STEP_CLICK:
                self.step_click(params)
        except:
            Logger.printexception()

    def substep1(self, params, formats):
        value = self.r.parse(formats, params.url)[0]
        Logger.getlogging().debug(value)
        type = value[0]
        sid = int(value[1])
        Logger.getlogging().debug(type)
        Logger.getlogging().debug(sid)
        #抓取播放量，youxi无播放量
        others = ['video','yule']
        if type in others:
            #针对娱乐中的专辑具体分析
            if params.originalurl.find('album') > 0:
                sid = int(self.albumfilter(params))
            url = self.CLICK_URL.format(type=type, id1=str(sid)[:3], id2=sid)
            self.storeurl(url, params.originalurl, KanKanComments.STEP_CLICK,{'sid': sid})
        else:
            Logger.getlogging().warning('{url} :40000 Sorry, {type} maybe others!'.format(url=params.url,type=type))
        #评论中的type转换
        type = self.typeconvert(value[0], params.url)
        commentinfo_url = KanKanComments.COMMENTS_URL2 % (type, sid, 1, self.PERPAGE)
        Logger.getlogging().debug(commentinfo_url)
        self.storeurl(commentinfo_url, params.originalurl, KanKanComments.STEP_2, {'type': type, 'sid': sid})
        
    def step2(self, params):
        # Step2: 通过Step1设置url，得到评论的总数和最后一次评论时间,并根据评论总数得到获取其他评论的url。
        content = params.content
        if "{" not in content:
            Logger.getlogging().debug('Get the data error')
            return
        jsonstr = content[content.index('{'):content.rindex('}')+1]
        commentsinfo = json.loads(jsonstr)
        comments_count = int(commentsinfo['data']['misc']['count'])
        Logger.getlogging().debug('{url} comment: {ct}'.format(url = params.url, ct = comments_count))
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        # 增量检查
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            return
        page_num = int(math.ceil(float(comments_count - cmtnum) / self.PERPAGE))
        if page_num >= self.maxpages:
            page_num = self.maxpages

        # 拼出获取评论的URL并保存
        if self.r.match(self.TYPE1, params.originalurl):
            movieid = params.customized['movieid']
            for page in range(1, page_num + 1, 1):
                if page == 1:
                    self.step3(params)
                    continue
                comment_url = KanKanComments.COMMENTS_URL1 .format (movieid=movieid, page = page,perpage=self.PERPAGE)
                self.storeurl(comment_url, params.originalurl, KanKanComments.STEP_3)
        elif self.r.match(self.TYPE2,params.originalurl):
            type = params.customized['type']
            sid = params.customized['sid']
            for page in range(1, page_num + 1, 1):
                if page == 1:
                    self.step3(params)
                    continue                        
                comment_url = KanKanComments.COMMENTS_URL2 % (type,sid,page,self.PERPAGE)
                self.storeurl(comment_url, params.originalurl, KanKanComments.STEP_3)
        elif self.r.match(self.TYPE3, params.originalurl):
            type = params.customized['type']
            sid = params.customized['sid']
            for page in range(1, page_num + 1, 1):
                if page == 1:
                    self.step3(params)
                    continue                        
                comment_url = KanKanComments.COMMENTS_URL2 % (type,sid,page,self.PERPAGE)
                self.storeurl(comment_url, params.originalurl, KanKanComments.STEP_3) 
                
    def step3(self, params):
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        commentsinfo = json.loads(params.content[2:-1])
        contents = commentsinfo['data']['weibo']
        for item in contents:
            curtime = TimeUtility.getuniformtime(item['pub_time'])
            content = item['content']
            nick = str(item['userinfo']['nickname'])
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

    
    #type2,type3模式下的播放量 
    def step_click(self,params):
        sid = params.customized['sid']
        infodata = json.loads(params.content)
        for info in infodata:
            if info['id']==str(sid):
                addtime = TimeUtility.getuniformtime(info['adddate'])
                playcount = self.str2num(info['playtimes'])
                NewsStorage.setclicknum(params.originalurl, playcount)
                NewsStorage.setpublishdate(params.originalurl, addtime)
                break
            
    #type1一般模式下的播放量 
    def setclicknum(self,params):
        pattern = 'var\sG_PLAY_VV\s=\s\{\stotal:\"(.*)\"\s\}'
        if self.r.search(pattern, params.content):
            playcount = self.r.parse(pattern, params.content)[0]
            playcount = playcount.replace(',','')
            pattern2 = 'subtype:\s(\[.*\])?,'
            if self.r.search(pattern2,params.content):
                subtype = self.r.parse(pattern2,params.content)[0]
                subtype = eval(subtype)
                num = self.count(subtype) 
                if num != 0:
                    playcount = int(playcount)/num
            NewsStorage.setclicknum(params.originalurl, playcount)
        
    #针对娱乐中的专辑具体分析
    def albumfilter(self, params):
        pattern = 'var\sG_SVOD_DATA_ALL\s=\s(.*);\nvar\sG_PLAY_ID'
        pattern2 = 'http://\w+\.kankan\.com/album/\d+/\d+\.shtml\?c=(\d+)'
        if re.search(pattern2, params.originalurl):
            return re.findall(pattern2, params.originalurl)[0]        
        elif re.search(pattern, params.content):
            data_all = re.findall(pattern, params.content)[0]
            #print data_all
            data = json.loads(data_all)
            return data[0]['id']
    ##############################################################################################
    # @functions：typeconvert
    # @type： 从url获取到的type种类
    # @return：newtype
    # @author：Hedian
    # @date：2016/12/19
    # @note：Bug修正用
    ##############################################################################################
    def typeconvert(self, type, url):
        suffix = ''
        if url.find('/album/') >= 0:
            suffix = '_album'
        if type == 'yule' or type == 'video':
            newtype = 'video' + suffix
            return newtype
        else:
            return type
    
    #只算主集，不算花絮或片花
    def count(self,lists):
        dicts = {}
        for item in lists:
            if int(item) == 1:
                dicts['1'] = dicts.get('1',0) + 1
        return dicts.get('1',0)
    
    UNITS = {u'万': 10000, u'亿': 100000000}
    def str2num(self, value):
        value = value.replace(',', '')
        multiplier = 1
        for unit in self.UNITS.keys():
            if unit in value:
                multiplier = self.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
            res = float(values[0]) * multiplier
        return int(res)   