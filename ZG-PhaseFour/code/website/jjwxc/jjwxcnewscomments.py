# -*- coding: utf-8 -*-
################################################################################################################
# @file: jjwxcnewscomments.py
# @author：JiangSiwei
# @date：2016/11/17
# @version: Ver0.0.0.100
# @note:
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
################################################################################################################

# from storage.commentsstorage import CommentInfo
from website.common.comments import SiteComments
from log.spiderlog import Logger
# from storage.urlsstorage import URLStorage
import json
from utility.gettimeutil import getuniformtime
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage
import ast


################################################################################################################
# @class：JjwxcNewsComments
# @author：JiangSiwei
# @date：2016/11/17
# @note：
################################################################################################################
class JjwxcNewsComments(SiteComments):

    # 晋江原创新闻S1需要的类变量
    # 2016/12/30 modified by hedian ---start
    # COMMENTS_URL = 'http://s8.static.jjwxc.net/comment_json.php?novelid={nid}'
    COMMENTS_URL = 'http://s8.static.jjwxc.net/comment_json.php?novelid={nid}&chapterid={cid}'
    # 2016/12/30 modified by hedian ---end

    NEWS_FIRST_PAGE = 'NEWS_FIRST_PAGE'
    NEWS_NEXT_PAGE = 'NEWS_NEXT_PAGE'


    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：JinjiangycNewscomments，初始化内部变量
    ################################################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ################################################################################################################
    # @functions：news_step1
    # @info： 获取评论的url
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def news_step1(self, params):
        """获取评论的url"""
        try:
            # 2016/12/30 modified by hedian ---start
            novelid_re = self.r.parse('.*novelid=(\d+).*', params.originalurl)
            if not novelid_re:
                return
            novelid = novelid_re[0]

            chapterid_re = self.r.parse('.*chapterid=(\d+).*', params.originalurl)
            if chapterid_re:
                chapterid = chapterid_re[0]
            else:
                chapterid = ''
            # 2016/12/30 modified by hedian ---end

            comment_url = self.COMMENTS_URL.format(nid=novelid, cid=chapterid)
            self.storeurl(comment_url, params.originalurl, self.NEWS_FIRST_PAGE)
        except:
            Logger.printexception()

    ################################################################################################################
    ################################################################################################################
    def news_step2(self, params):
        """通过评论的url获取评论"""
        try:
            jsondata = json.loads(params.content)
            for comment in jsondata['body']:
                content = str(comment['commentbody'])
                nick = str(comment['commentauthor'])
                curtime = TimeUtility.getuniformtime(comment['commentdate'])
                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)

                if int(comment['reply_total']) > 0:
                    for index in range(0, int(comment['reply_total']), 1):
                        content = comment['reply'][index]['commentbody']
                        curtime = TimeUtility.getuniformtime(comment['reply'][index]['commentdate'])
                        nick = comment['reply'][index]['commentauthor']
                        if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                            CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()