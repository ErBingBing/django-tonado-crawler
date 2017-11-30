# coding=utf-8
################################################################################################################
# @file: sinacomments.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
# @modify
# @author:Jiangsiwei
# @date:2017/02/08
# @note:第178-184行添加了对播放量取不到时的异常处理
# @date:2017/02/20
# @note:修改sinacomments.py中代码第118-120行，添加为类似取newid的过程; 修改sinacomments.py中代码第125行，重新设置pn参数
#       comments_url = CommonComments.SINA_COMMENTS_URL.format(channel=channel, newsid=newsid, pn=1, ps=1)中参数pn=20
################################################################################################################
import json
import math
import re

from configuration.constant import CHARSET_UTF8
from log.spiderlog import Logger
from storage.cmtstorage import CMTStorage
from utility.common import Common
from utility.regexutil import RegexUtility
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from utility.timeutility import TimeUtility


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class SinaComments(SiteComments):
    # PATTERNS
    VIDEO_PATTERN_TYPE = 'video'  # 视频
    BLOG_PATTERN_TYPE = 'blog'  # 博客
    MANHUA_PATTERN_TYPE = 'mahua'  # 漫画
    STGP_PATTERN_TYPE = 'sgtp'  # 体育 游戏 旅游 图片
    COMMON_PATTERN_TYPE = 'common'

    REGEX_PATTERNS = {
        VIDEO_PATTERN_TYPE: r'^http://video\.sina\.com\.cn.*',
        BLOG_PATTERN_TYPE: r'^http://blog\.sina\.com\.cn.*',
        MANHUA_PATTERN_TYPE: r'^http://manhua\.weibo\.com\.cn.*',
        STGP_PATTERN_TYPE: r'^http://(sports|travel|games|photo)\.sina\.com\.cn.*',
    }

    # 默认页面回复条数
    DEFAULT_PAGE_SIE = 100

    # VIDEO获取页面的
    STEP_DEFAULT_VALUE = None
    STEP_CLICK_PAGE = 1
    STEP_COMMENT_FIRST_PAGE = 2
    STEP_COMMENT_NEXT_PAGE = 3

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteComments.__init__(self)

    ################################################################################################################
    # @functions：process
    # @param： params
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def process(self, params):
        type = SinaComments.COMMON_PATTERN_TYPE
        for key in SinaComments.REGEX_PATTERNS.keys():
            if RegexUtility.match(SinaComments.REGEX_PATTERNS[key], params.originalurl):
                type = key
        Logger.getlogging().debug('{url}:{key}'.format(url=params.originalurl, key=type))
        if type == SinaComments.VIDEO_PATTERN_TYPE:
            CommonComments(self).process(params)
        elif type == SinaComments.BLOG_PATTERN_TYPE:
            BlogComments(self).process(params)
        elif type == SinaComments.MANHUA_PATTERN_TYPE:
            self.manhuaprocess(params)
        elif type == SinaComments.STGP_PATTERN_TYPE:
            CommonComments(self).process(params)
        else:
            CommonComments(self).process(params)


class CommonComments(SinaComments):
    SINA_COMMENTS_URL = 'http://comment5.news.sina.com.cn/page/info?channel={channel}&newsid={newsid}&page={pn}&page_size={ps}'
    SINA_CLICKNUM_URL = 'http://count.video.sina.com.cn/getVideoView?video_ids={video_id}'
    SINA_BLOG_COMMENTS_URL = 'http://blog.sina.com.cn/s/comment_{articleid}_{page}.html?comment_v=articlenew'

    def __init__(self, parent):
        SinaComments.__init__(self)
        self.website = parent.website

    def process(self, params):
        if params.step is None:
            self.step1(params)
        elif params.step == SinaComments.STEP_COMMENT_FIRST_PAGE:
            self.step2(params)
        elif params.step == SinaComments.STEP_COMMENT_NEXT_PAGE:
            self.step3(params)
        elif params.step == SinaComments.STEP_CLICK_PAGE:
            self.get_video_clicknum(params)

    def step1(self, params):
        newsid = self.r.getid('newsid', params.content, ':')
        if not newsid:
            newsid = self.r.getid('newsid', params.content, '=')
        channel = self.r.getid('channel', params.content,':')
        if not channel:
            channel = self.r.getid('channel', params.content, '=')        
        if not newsid or not channel:
            return
        # 修正体育频道newsid名称错误，正确为'comos-fykuffc5598034',从params.content获取到的为'conmos-fykuffc5598034'
        if channel == 'ty':
            newsid = newsid.replace('n','')

        comments_url = CommonComments.SINA_COMMENTS_URL.format(channel=channel, newsid=newsid, pn=1, ps=20)
        group = self.r.getid('group', params.content)
        if group:
            comments_url = comments_url + '&group=' + group

        self.storeurl(comments_url, params.originalurl, SinaComments.STEP_COMMENT_FIRST_PAGE,
                      {'newsid': newsid, 'channel': channel, 'group': group})
        if self.r.search('http[s]{0,1}://.*video\.sina\.com.*', params.originalurl):
            # video_id = params.originalurl.split('/')[-1].split('.')[0]
            video_id = self.r.getid('video_id', params.content, ':')
            if video_id:
                click_url = CommonComments.SINA_CLICKNUM_URL.format(video_id=video_id)
                self.storeurl(click_url, params.originalurl, SinaComments.STEP_CLICK_PAGE,
                              {'video_id': video_id})

    def step2(self, params):
        newsid = params.customized['newsid']
        channel = params.customized['channel']
        group = params.customized['group']
        comments = json.loads(params.content)
        if not self.isvalid(comments):
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        # 获取视频的publishdate
        if self.r.search('http[s]{0,1}://.*video\.sina\.com.*', params.originalurl):
            publishdate = comments['result']['news']['time']
            NewsStorage.setpublishdate(params.originalurl, TimeUtility.getuniformtime(publishdate))
        # 获取新闻的clicknum
        elif self.r.search('http[s]{0,1}://.*\.sina\.com.*', params.originalurl):
            if NewsStorage.getclicknum(params.originalurl) <= 0:
                try:
                    news_clicknum = comments['result']['count']['total']
                    NewsStorage.setclicknum(params.originalurl, news_clicknum)
                except:
                    Logger.printexception()
        comments_count = int(comments['result']['count']['show'])
        #设置cmtnum
        NewsStorage.setcmtnum(params.originalurl, comments_count)

        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comments_count:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        pages = int(math.ceil(float(comments_count - cmtnum) / self.DEFAULT_PAGE_SIE))
        if pages >= self.maxpages:
            pages = self.maxpages
        for page in range(1, pages + 1, 1):
            if page == 1:
                self.step3(params)
                continue
            url = CommonComments.SINA_COMMENTS_URL.format(channel=channel, newsid=newsid, pn=page,
                                                          ps=SinaComments.DEFAULT_PAGE_SIE)
            if group:
                url = url + '&group=' + group
            self.storeurl(url, params.originalurl, SinaComments.STEP_COMMENT_NEXT_PAGE)

    def step3(self, params):
        try:
            Logger.getlogging().debug(params.originalurl)
            data = json.loads(params.content)
            if not self.isvalid(data):
                Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
                return
            for it in data['result']['cmntlist']:
                # Logger.getlogging().debug(it['content'])
                # 保存评论到数据库，可以通过接口exist判断评论是否已经存在
                content = it['content']
                curtime = TimeUtility.getuniformtime(it['time'])
                try:
                    nick = it['nick']
                except:
                    nick = 'anonymous'
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)

        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site=params.url))

    def isvalid(self, jsondata):
        if int(jsondata['result']['status']['code']) <> 0:
            Logger.getlogging().warning(jsondata['result']['status']['msg'])
            return False
        return True

    def get_video_clicknum(self, params):
        try:
            data = json.loads(params.content)
            video_id = params.customized['video_id']
            video_clicknum = int(data['data']['video_id'][video_id])
        except:
            Logger.getlogging().warning('{}:30001'.format(params.originalurl))
            return
        NewsStorage.setclicknum(params.originalurl, video_clicknum)


class BlogComments(SinaComments):
    SINA_BLOG_COMMENTS_URL = 'http://blog.sina.com.cn/s/comment_{articleid}_{page}.html?comment_v=articlenew'
    limit = 50

    def __init__(self, parent):
        SinaComments.__init__(self)
        self.website = parent.website

    def process(self, params):
        if params.step is None:
            self.step1(params)
        elif params.step == SinaComments.STEP_COMMENT_FIRST_PAGE:
            self.step2(params)
        elif params.step == SinaComments.STEP_COMMENT_NEXT_PAGE:
            self.step3(params)

    def step1(self, params):
        # 根据输入内容, 得到articleid
        articleid = self.r.getid('articleid', params.content)
        if not articleid:
            articleid = self.getarticleid(params.originalurl)
            if not articleid:
                return

        comments_url = BlogComments.SINA_BLOG_COMMENTS_URL.format(articleid=articleid, page=1)
        self.storeurl(comments_url, params.originalurl, SinaComments.STEP_COMMENT_FIRST_PAGE, {'articleid': articleid})

    def step2(self, params):
        articleid = params.customized['articleid']
        jsondata = json.loads(params.content)
        comment_total_num = int(jsondata['data']['comment_total_num'])
        NewsStorage.setcmtnum(params.originalurl, comment_total_num)
        # 检查评论是否有更新
        cmtnum = CMTStorage.getcount(params.originalurl, True)
        if cmtnum >= comment_total_num:
            Logger.getlogging().warning('{url}:30000 No comments'.format(url=params.originalurl))
            return
        pages = int(math.ceil(float(comment_total_num - cmtnum) / self.limit))
        if pages >= self.maxpages:
            pages = self.maxpages
        for page in range(1, pages + 1, 1):
            if page == 1:
                # 获取第一页的评论
                self.geturlcomemnts(params)
                continue
        # 获取其他页的评论
            comments_url = BlogComments.SINA_BLOG_COMMENTS_URL.format(articleid=articleid, page=page)
            self.storeurl(comments_url, params.originalurl, SinaComments.STEP_COMMENT_NEXT_PAGE)

    def step3(self, params):
        self.geturlcomemnts(params)

    def getarticleid(self, url):
        # url = blog.sina.com.cn/s/blog_7159859d0102x3cu.html?tj=1
        pattern = 'blog_(.*)\.html.*'
        articleids = None
        if self.r.search(pattern,url):
            articleids = self.r.parse(pattern,url)[-1]
        return articleids
    
    def geturlcomemnts(self, params):
        Logger.getlogging().debug(params.originalurl)
        jsondata = json.loads(params.content)
        for it in jsondata['data']['comment_data']:
            content = Common.urldec(it['cms_body']).decode(CHARSET_UTF8)
            content = self.filterstr(content)
            Logger.getlogging().debug(content)
            if not CMTStorage.exist(params.originalurl, content, it['cms_pubdate'], it['uname']):
                CMTStorage.storecmt(params.originalurl, content, it['cms_pubdate'], it['uname'])

    @staticmethod
    def filterstr(s):
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

    def getclicknum(self, params):
        try:
            data = json.loads(params.content)
            video_id = params.customized['video_id']
            clicknum = int(data['data']['video_id'][video_id])
        except:
            Logger.getlogging().warning('{}:30001'.format(params.originalurl))
            return
        NewsStorage.setclicknum(params.originalurl, clicknum)