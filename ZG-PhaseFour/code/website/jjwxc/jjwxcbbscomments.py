# -*- coding: utf-8 -*-
################################################################################################################
# @file: jjwxcbbscomments.py
# @author: HuBorui
# @date:  2016/12/05
# @version: Ver0.0.0.100
# @note:
# @修改日志
# @author：yongjicao
# @date：2017/9/12
# @note：修改评论存储方式为mysql
################################################################################################################
#from storage.commentsstorage import CommentInfo
#from storage.urlsstorage import URLStorage, URLCommentInfo
from utility.xpathutil import XPathUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
import traceback
from storage.cmtstorage import CMTStorage
from utility.timeutility import TimeUtility
from storage.newsstorage import NewsStorage


################################################################################################################
# @class：JjwxcBbsComments
# @author: HuBorui
# @date:  2016/12/05
# @note：
################################################################################################################
class JjwxcBbsComments(SiteComments):
    COMMENTS_URL = '{url}&page={pageno}'
    BBS_NEXT_PAGE = 'BBS_NEXT_PAGE'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：JinjiangycBbscomments，初始化内部变量
    ################################################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ################################################################################################################
    # @functions：jinjiangycbbs_step1
    # @info：none
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    # def jinjiangycbbs_step1(self,params):
    #     self.storeurl(params.originalurl, params.originalurl, self.JINJIANGYC_BBS_FIRST_PAGE)

    ################################################################################################################
    # @functions：bbs_step2
    # @params： 下载平台传回的下载结果等信息
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def bbs_step2(self, params):
        try:
            xparser = XPathUtility(params.content)
            comment_counts = int(xparser.getnumber('//*[@id="msgsubject"]/font'))
            if comment_counts == 0:
                return
            cmtnum = CMTStorage.getcount(params.originalurl, True)
            # 判断增量
            if cmtnum >= comment_counts:
                return
            pagecount = xparser.getnumber('//*[@id="pager_top"]')

            for page in range(0, pagecount + 1, 1):
                commentUrl = JjwxcBbsComments.COMMENTS_URL.format(url=params.originalurl, pageno=page)
                Logger.getlogging().debug(commentUrl)
                self.storeurl(commentUrl, params.originalurl, JjwxcBbsComments.BBS_NEXT_PAGE, {'page': page,'pagecount':pagecount})
                NewsStorage.setcmtnum(params.originalurl, comment_counts)
        except Exception, e:
            traceback.print_exc()
    ################################################################################################################
    # @functions：bbs_step3
    # @params： 获取每页的具体信息
    # @return：none
    # @note：SiteComments，S1 comments
    ################################################################################################################
    def bbs_step3(self, params):
        try:
            xparser = XPathUtility(params.content)
            page = params.customized['page']
            pagecount = params.customized['pagecount']
            comments = []
            updatetimes = []
            nicks = []
            contents = xparser.getcomments('//*[@class="read"]')
            mid_times = xparser.getlist('//td[@class="authorname"]')
            for times in mid_times:
                updatetimes.append(self.r.parse(ur'于(\d+-\d+-\d+ \d+:\d+:\d+)留言', times)[0])
                nicks.append(self.r.parse(ur'(.*)于', times)[0])
            if page == 0:
                mid_index = 1
            elif page > 0:
                mid_index = 0
            comments_number = xparser.getnumber('//*[@id="msgsubject"]/font')
            if comments_number != 0:
                for index in range(mid_index, len(contents), 1):
                    curtime = TimeUtility.getuniformtime(updatetimes[index])
                    content = contents[index]
                    nick = nicks[index].split('于')[0].split('☆')[-1]
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except Exception, e:
            traceback.print_exc()


