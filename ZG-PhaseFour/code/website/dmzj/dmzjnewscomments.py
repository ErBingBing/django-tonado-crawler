# -*- coding: utf-8 -*-
################################################################################################################
# @file: dmzjvideocomments.py
# @author：Yuxiaoye
# @date：2016/12/16
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import math

from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
import json
from log.spiderlog import Logger
################################################################################################################
# @class：DmzjNewscomments
# @author：Yuxiaoye
# @date：2016/12/16
# @note：
################################################################################################################
class DmzjNewscomments(SiteComments):

    # 动漫之家新闻S1需要的类变量
    NEW_URL_REG = 'https://interface.dmzj.com/api/NewComment2/list?type={commment_type}&obj_id={comic_id}&page_index={index}'
    # NEWS_TOTALCOUNT_URL = 'http[s]{0,1}://interface.dmzj.com/api/NewComment2/total?callback=s_0&&type={commment_type}&obj_id={comic_id}&authorId={authorId}'
    NEWS_TOTALCOUNT_URL = 'https://interface.dmzj.com/api/NewComment2/total?type={commment_type}&obj_id={comic_id}'

    DMZJ_NEWS_FIRST_PAGE = 'DMZJ_NEWS_FIRST_PAGE'
    DMZJ_NEWS_NEXT_PAGE = 'DMZJ_NEWS_NEXT_PAGE'
    DEFAULT_PAGE_SIZE = 30
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：DmzjNewscomments，初始化内部变量
    ################################################################################################################
    def __init__(self, parent=None):
        SiteComments.__init__(self)
        if parent:
            self.website = parent.website

    ################################################################################################################
    # @functions：dmzjnews_step1
    # @info： 获取评论的url
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def dmzjnews_step1(self, params):
        if self.r.match('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl):
            field = self.r.parse('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl)[0]
        else:
            field = self.r.parse('^http[s]{0,1}://(\w+).dmzj.com/.*', params.originalurl)[0]
        if field == 'news':
            comment_type = self.r.getid('comment_type', params.content, '\s*=\s*')
            if not comment_type:
                comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            comic_id = self.r.parse('article/(\d+)', params.originalurl)[0]
        elif field == 'manhua':
            comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            if not comment_type:
                comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            comic_id = self.r.getid('obj_id', params.content, '\s*=\s*')
        elif field == 'xl':
            comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            if not comment_type:
                comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            comic_id = self.r.parse('com/(\d+)', params.originalurl)[0]
        elif field == 'info':
            comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            if not comment_type:
                comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            comic_id = self.r.getid('comic_id', params.content, '\s*=\s*')
        elif field == 'donghua':
            comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
            comic_id = self.r.parse('info/(\d+)', params.originalurl)[0]
        comments_url = DmzjNewscomments.NEWS_TOTALCOUNT_URL.format(commment_type = comment_type, comic_id = comic_id)
        self.storeurl(comments_url, params.originalurl, DmzjNewscomments.DMZJ_NEWS_FIRST_PAGE, {'comic_id': comic_id,'comment_type' : comment_type})

    ################################################################################################################
    # @functions：dmzjinfo_step1
    # @info： 获取评论的url
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    # def dmzjinfo_step1(self, params):
    #     comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     if not comment_type:
    #         comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     authorId = self.r.getid('authoruid', params.content, '\s*=\s*')
    #     comic_id = self.r.getid('comic_id', params.content, '\s*=\s*')
    #     comments_url = DmzjNewscomments.NEWS_TOTALCOUNT_URL.format(commment_type=comment_type, comic_id=comic_id,index =1)
    #     self.storeurl(comments_url, params.originalurl, DmzjNewscomments.DMZJ_NEWS_FIRST_PAGE,
    #                   {'comic_id': comic_id, 'comment_type': comment_type})
    #
    # ################################################################################################################
    # # @functions：dmzjmanhua_step1
    # # @info： 获取评论的url
    # # @return：none
    # # @note：SiteComments，S1 comments
    # ################################################################################################################
    # def dmzjmanhua_step1(self, params):
    #     comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     if not comment_type:
    #         comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     authorId = self.r.getid('authoruid', params.content, '\s*=\s*')
    #     comic_id = self.r.getid('obj_id', params.content, '\s*=\s*')
    #     comments_url = DmzjNewscomments.NEWS_TOTALCOUNT_URL.format(commment_type=comment_type, comic_id = comic_id , authorId=authorId)
    #     self.storeurl(comments_url, params.originalurl, DmzjNewscomments.DMZJ_NEWS_FIRST_PAGE, {'comic_id': comic_id  , 'comment_type': comment_type})
    #
    # ################################################################################################################
    # # @functions：dmzjxs_step1
    # # @info： 获取评论的url
    # # @return：none
    # # @note：SiteComments，S1 comments
    # ################################################################################################################
    # def dmzjxs_step1(self, params):
    #     comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     if not comment_type:
    #         comment_type = self.r.getid('commment_type', params.content, '\s*=\s*')
    #     authorId = self.r.getid('authoruid', params.content, '\s*=\s*')
    #     comic_id = self.r.parse('com/(\d+)', params.originalurl)[0]
    #     comments_url = DmzjNewscomments.NEWS_TOTALCOUNT_URL.format(commment_type=comment_type, comic_id=comic_id,
    #                                                                authorId=authorId)
    #     self.storeurl(comments_url, params.originalurl, DmzjNewscomments.DMZJ_NEWS_FIRST_PAGE,
    #                   {'comic_id': comic_id, 'comment_type': comment_type})

    ################################################################################################################
    # @functions：step2bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/16
    # @note：根据输入html，得到评论总量，拼出获取评论的url
    ################################################################################################################
    def dmzjnews_step2(self, params):
        comic_id = params.customized['comic_id']
        comment_type = params.customized['comment_type']
        #获取总评论数
        params.content = params.content[params.content.index('{') : params.content.rindex('}') + 1]
        countinfo = json.loads(params.content)
        try:
            curcmtnum = countinfo['data']
        except:
            Logger.getlogging().warning('Site not found for {url}'.format(url=params.originalurl))
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        if dbcmtnum >= curcmtnum:
            return
        pages = int(math.ceil(float(curcmtnum-dbcmtnum)/self.DEFAULT_PAGE_SIZE))
        #获取总页数
        if pages >= self.maxpages:
            pages = self.maxpages
        for index in range(1, pages + 1, 1):
            comments_url = DmzjNewscomments.NEW_URL_REG.format(commment_type=comment_type, comic_id=comic_id, index=index)
            self.storeurl(comments_url, params.originalurl, DmzjNewscomments.DMZJ_NEWS_NEXT_PAGE)

    ################################################################################################################
    # @functions：step3bbs
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：无
    # @author：YuXiaoye
    # @date：2016/12/16
    # @note：根据输入的html(json文件），得到评论
    ################################################################################################################
    def dmzjnews_step3(self, params):
        params.content = params.content[params.content.index('['):params.content.rindex(']') + 1]
        commentsinfo = json.loads(params.content)
        for index in range(0, len(commentsinfo), 1):
            # 提取时间
            content = commentsinfo[index]['content']
            curtime = TimeUtility.getuniformtime(commentsinfo[index]['create_time'])
            CMTStorage.storecmt(params.originalurl, content, curtime, '')

    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == None:
            # if self.r.match('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl):
            #     field = self.r.parse('^http[s]{0,1}://www\.dmzj\.com\/(\w+)', params.originalurl)[0]
            # else:
            #     field = self.r.parse('^http[s]{0,1}://(\w+).dmzj.com/.*', params.originalurl)[0]
            # if field == 'news':
            #     self.dmzjnews_step1(params)
            # if field == 'manhua':
            #     self.dmzjmanhua_step1(params)
            # if field == 'xl':
            #     self.dmzjxs_step1(params)
            # if field == 'info':
            #     self.dmzjinfo_step1(params)
            self.dmzjnews_step1(params)
        elif params.step == DmzjNewscomments.DMZJ_NEWS_FIRST_PAGE:
            self.dmzjnews_step2(params)

        elif params.step == DmzjNewscomments.DMZJ_NEWS_NEXT_PAGE:
            self.dmzjnews_step3(params)        
        
