# coding=utf-8

##############################################################################################
# @file：yueducomments.py
# @author：Hedian
# @date：2016/12/05
# @version：Ver0.0.0.100
# @note：网易云阅读获取评论的文件
##############################################################r################################
from utility.gettimeutil import getuniformtime
from utility.gettimeutil import TimeUtility
from website.common.comments import SiteComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
import json
import datetime
import math
import time
import re
from log.spiderlog import Logger 

##############################################################################################
# @class：YueduComments
# @author：Hedian
# @date：2016/12/05
# @note：网易云阅读取评论的类，继承于SiteComments类
##############################################################################################
class YueduComments(SiteComments):
    COMMENT_URL = 'http://yuedu.163.com/snsComment.do?operation=get&type={types}&id={id}&page={pageno}&pageSize=20'
    YUEDU_STEP_1 = None
    YUEDU_STEP_2 = 'YUEDU_STEP_2'
    YUEDU_STEP_3 = 'YUEDU_STEP_3'
    PAGE_SIZE = 20

    ##############################################################################################
    # @functions：__init__
    # @return：none
    # @author：Hedian
    # @date：2016/12/05
    # @note：YueduComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website
        
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        if params.step == YueduComments.YUEDU_STEP_1:
            self.yuedu_step1(params)
        elif params.step == YueduComments.YUEDU_STEP_2:
            self.yuedu_step2(params)
        elif params.step == YueduComments.YUEDU_STEP_3:
            self.getyueduurlcomment(params)
        
        

    ################################################################################################################
    # @functions：yuedu_step1
    # @proparam：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @note：
    ################################################################################################################
    def yuedu_step1(self, params):
        # 网易云阅读处理
        field= self.r.parse('^http://.*yuedu.163.com/(.*?)/.*', params.originalurl)[0]
        if field == "source":
            idvalue = self.r.parse('^http://.*yuedu.163.com/source/(\w+_\d)', params.originalurl)[0]
            commentinfo_url = YueduComments.COMMENT_URL.format(types='2',id=idvalue, pageno='1')
            self.storeurl(commentinfo_url, params.originalurl, YueduComments.YUEDU_STEP_2, {'id': idvalue, 'field': 'yuedu','types':'2'})            
        else:
            idvalue2 = re.findall('(\w+_\d+)', params.originalurl)[1]
            idvalue3 = re.findall('(\w+_\d+)', params.originalurl)[0]
            commentinfo_url2 = YueduComments.COMMENT_URL.format(types='0',id=idvalue2, pageno='1')
            commentinfo_url3 = YueduComments.COMMENT_URL.format(types='1',id=idvalue3, pageno='1')
            self.storeurl(commentinfo_url3, params.originalurl, YueduComments.YUEDU_STEP_2, {'id': idvalue3, 'field': 'yuedu','types':'1'})
            self.storeurl(commentinfo_url2, params.originalurl, YueduComments.YUEDU_STEP_2, {'id': idvalue2, 'field': 'yuedu','types':'0'})
        try:
            clicknum = self.r.parse(ur'<td>点击：</td><td>(.*?)</td>',params.content)[0]
            clicknum = self.str2num(clicknum)
            Logger.getlogging().debug('{url} clicknum:{clicknum}'.format(url=params.originalurl, clicknum=clicknum))
            NewsStorage.setclicknum(params.originalurl, clicknum)

        except:
            Logger.printexception()
            

    ##############################################################################################
    # @functions：yuedu_step2
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：Hedian
    # @date：2016/12/05
    # @note：
    ##############################################################################################
    def yuedu_step2(self, params):
        # 网易云阅读处理
        idvalue = params.customized['id']
        # 获取第一页url的评论,返回总页数
        try:
            commentsinfo = json.loads(params.content)
            # 获取当前的评论总量
            totalCount = int(commentsinfo['totalCount'])
            NewsStorage.setcmtnum(params.originalurl, totalCount)
        except:
            Logger.getlogging().warning('{0}:30000 No comments'.format(params.originalurl))
            return 

        if totalCount == 0:
            # 没有评论返回
            return

        # 检查上次抓取的评论总量是否变化，没有变化，返回。变化则更新
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= totalCount:
            return
        max = int(math.ceil(float(totalCount - cmtnum) / self.PAGE_SIZE))
        if max > self.maxpages:
            max = self.maxpages

        # # 获取第一页的评论
        # try:
        #     self.getyueduurlcomment(params)
        # except:
        #     Logger.printexception()
        #     Logger.getlogging().error('extract comment error from {site}'.format(site=params.url))


        # totalpages = int(commentsinfo['totalPage'])
        # 得到其他评论的url（第一页已经获取成功，从第二页开始）
        for page in range(1, max + 1, 1):
            if page == 1:
                self.getyueduurlcomment(params)
                continue
            commentinfo_url = YueduComments.COMMENT_URL.format(types=params.customized['types'],id=idvalue, pageno=page)
            self.storeurl(commentinfo_url, params.originalurl, YueduComments.YUEDU_STEP_3, {'id': idvalue, 'field': 'yuedu','types':params.customized['types']})

    ##############################################################################################
    # @functions：getdatetime
    # @param：时间字符串
    # @return：标准时间字符串 YYYY-MM-DD HH:MM
    # @author：Hedian
    # @date：2016/11/18
    # @note：把非标准的时间字符串转化为标准字符串。
    ##############################################################################################
    def getdatetime(self, datetime):
        if self.r.search(u'^\d+-\d+-\d+\s+\d+:\d+?', datetime):
            return datetime

        loctime = time.localtime()
        year = loctime[0]
        if self.r.search(u'\d+月\d+日\s+\d+:\d+?', datetime):
            value = self.r.parse(u'(\d+)月(\d+)日\s+(\d+:\d+)?', datetime)[0]
            newdatetime = '{year}-{month}-{day} {time}'.format(year=year, month=value[0], day=value[1], time=value[2])
            return newdatetime

        if self.r.search(u'^\d+-\d+-\d+?', datetime):
            value = self.r.parse(u'^(\d+-\d+-\d+)?', datetime)[0]
            newdatetime = '{date} 00:00'.format(date=value)
            return newdatetime

    ##############################################################################################
    # @functions：getyueduurlcomment
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：评论总页数
    # @author：Hedian
    # @date：2016/11/18
    # @note：获取一页url的评论
    ##############################################################################################
    def getyueduurlcomment(self, proparam):
        try:
            commentsinfo = json.loads(proparam.content)

            for key in commentsinfo['data']:
                # cmti = CommentInfo()
                # 得到标准日期格式
                #posttime = self.getdatetime(key['posttime'].strip())
                #if posttime is None:
                curtime= TimeUtility.getuniformtime(key['posttime'].strip())
                content =  key['text']
                nick = key['username']
                if not CMTStorage.exist(proparam.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(proparam.originalurl, content, curtime, nick)
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site=proparam.url))

                #     if URLStorage.storeupdatetime(proparam.originalurl,posttime):
        #         cmti.content = key['text']
        #         comments.append(cmti)
        #
        # if len(comments) > 0:
        #     self.commentstorage.store(proparam.originalurl, comments)

    UNITS = {u'万': 10000, u'亿': 100000000, u'W': 10000}

    def str2num(self, value):
        value = value.replace('.', '')
        multiplier = 1
        for unit in self.UNITS.keys():
            if unit in value:
                multiplier = self.UNITS[unit]
        values = re.findall(r'\d+[.]?\d*', value)
        res = -1
        if values:
            res = float(values[0]) * multiplier
        return int(res)

