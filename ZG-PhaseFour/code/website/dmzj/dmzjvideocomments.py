# -*- coding: utf-8 -*-
################################################################################################################
# @file: dmzjvideocomments.py
# @author：
# @date：2016/12/06
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import math
import datetime
from lxml import etree
from storage.newsstorage import NewsStorage
from storage.cmtstorage import CMTStorage
from utility.gettimeutil import getuniformtime
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
import json
from bs4  import BeautifulSoup 
from log.spiderlog  import Logger 

################################################################################################################
# @class：DmzjVideocomments
# @author：
# @date：2016/12/06
# @note：
################################################################################################################
class DmzjVideocomments(SiteComments):

    # 动漫之家视频S1需要的类变量
    COMMENTS_URL = 'https://s.acg.dmzj.com/dh/index.php?c=comment&e={filename}&p={pgno}&m=showList'

    DMZJ_VIDEO_FIRST_PAGE = 'DMZJ_VIDEO_FIRST_PAGE'
    DMZJ_VIDEO_NEXT_PAGE = 'DMZJ_VIDEO_NEXT_PAGE'
    DEFAULT_PAGE_SIZE = 10
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
    def dmzjvideo_step1(self, params):
        # 1. 根据输入原始url, 拼出评论首页
        # http://donghua.dmzj.com/donghua_play/262838.html
        filename = self.r.parse('^http[s]{0,1}://\w+\.dmzj\.com/donghua_\w+/(\w+)\.html?', params.originalurl)[0]
        comments_url = DmzjVideocomments.COMMENTS_URL.format(filename=filename, pgno=1)
        self.storeurl(comments_url, params.originalurl, DmzjVideocomments.DMZJ_VIDEO_FIRST_PAGE, {'filename': filename})

    ################################################################################################################
    ################################################################################################################
    def dmzjvideo_step2(self, params):
        # 通过xpath, 从页面上获取评论总量
        html = etree.HTML(params.content)
        curcmtnum = float(html.xpath('//*[@id="onlinereplycountdiv"]')[0].text)
        dbcmtnum = CMTStorage.getcount(params.originalurl, True)
        NewsStorage.setcmtnum(params.originalurl, curcmtnum) 
        if dbcmtnum >= curcmtnum:
            return
        pages = int(math.ceil(float(curcmtnum-dbcmtnum)/self.DEFAULT_PAGE_SIZE))
        if pages == 0:
            pages = 1

         # 评出获取评论的所有页面
        filename = params.customized['filename']
        for page in range(1, pages + 1, 1):
            url = DmzjVideocomments.COMMENTS_URL.format(filename=filename, pgno=page)
            self.storeurl(url, params.originalurl, DmzjVideocomments.DMZJ_VIDEO_NEXT_PAGE)

    ################################################################################################################
    ################################################################################################################
    def dmzjvideo_step3(self, params):
        soup = BeautifulSoup(params.content,  'html5lib')
        divs = soup.select('#comment_list_div > .online_anim_debate_mr')
        for div in divs:
            try:
                updatetime = div.select_one('.anim_debate_mr_right_title').get_text()
                content = div.select_one('.anim_debate_mr_right_mr').get_text()
                CMTStorage.storecmt(params.originalurl, content, TimeUtility.getuniformtime(updatetime), '')
            except:
                Logger.printexception()    
    #----------------------------------------------------------------------
    def process(self,params):
        """"""
        if params.step == None:
            self.dmzjvideo_step1(params)
        if params.step == DmzjVideocomments.DMZJ_VIDEO_FIRST_PAGE:
            self.dmzjvideo_step2(params)
        if params.step == DmzjVideocomments.DMZJ_VIDEO_NEXT_PAGE:
            self.dmzjvideo_step3(params)        
        