# encoding=utf8

##############################################################################################
# @file：ZolbbsComments.py
# @author：QW_Liang
# @date：2017/9/16
# @version：Ver0.0.0.100
# @note：中关村论坛获取评论的文件
##############################################################################################

import json
import math
import datetime
import traceback
import time
from utility.xpathutil import XPathUtility
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from log.spiderlog import Logger
from  lxml  import  etree
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
##############################################################################################
# @class：ZolbbsComments
# @author：QW_Liang
# @date：2017/9/16
# @note：中关村论坛获取评论的类，继承于WebSite类
##############################################################################################
class ZolbbsComments(SiteComments):
    COMMENT_URL ='http://bbs.zol.com.cn/{field}/d{boardid}_{bookid}_{page}.html'
    FORMAT = 'http://bbs.zol.com.cn/(\w+)/d(\d+)_(\d+)(_\d+)?\.html'
    STEP_1 = None
    STEP_2 = 2
    PAGE_SIZE = 20

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：ZolbbsComments类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self, parent):
        SiteComments.__init__(self)
        self.website = parent.website

    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：Step1：获取评论的首页url
    #          Step2：获取评论的所有url
    #          Step3: 抽出的评论和最新评论的创建时间
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：Step1：通过共通模块传入的html内容获取到boradid,bookid,拼出获取评论总数的url，并传递给共通模块
    #        Step2：通过共通模块传入的html内容获取到评论总数，拼出获取评论的url，并传递给共通模块
    ##############################################################################################
    def process(self, params):
        Logger.getlogging().info(params.url)
        try:
            if params.step is ZolbbsComments.STEP_1:
                 #Step1: 通过得到docurl，得到获取评论的首页url。
                 if not self.r.search(self.FORMAT,params.originalurl):
                     Logger.getlogging().error(params.originalurl)
                     return
                 value = self.r.parse(self.FORMAT,params.originalurl)[0]
                 field = value[0]
                 boardid = value[1]
                 bookid = value[2]

                 # 默认为第一页
                 curpage = 1
                 if len(value) > 3:
                     if value[3] == '':
                         pass
                     else:
                         curpage = int(value[3][1:])

                 # 获取总页数
                 totalpagestr = self.r.getid('totalPage', params.content)
                 if totalpagestr == '':
                     Logger.getlogging().error('Unable to get totalPage')
                     return

                 # 打开STEP1中URL，截取"count"：num字段，取出num的值，num字段为评论总数
                 html = etree.HTML(params.content)
                 xparser = XPathUtility(params.content)
                 # 论坛评论数
                 comments_count = int(xparser.getnumber('//*[@id="bookTitle"]/div/em[2]'))
                 if comments_count == 0:
                     return
                 cmtnum = CMTStorage.getcount(params.originalurl,True)
                 if cmtnum >= comments_count:
                     return
                 # 保存最新评论数
                 NewsStorage.setcmtnum(params.originalurl, comments_count)

                 # 获取当前页的评论
                 params.customized['page'] = curpage
                 self.geturlcomments(params)

                 # 拼出其他评论页面
                 totalPage = int(totalpagestr)
                 # 做爬取最大页数判断
                 if totalPage >= self.maxpages:
                     totalPage = self.maxpages

                 start = int(cmtnum / self.PAGE_SIZE) + 1
                 end = int(totalPage)
                 if end > start + self.maxpages:
                     start = end - self.maxpages

                 for page in range(end, start - 1, -1):
                     if page == curpage:
                         continue
                     comment_url = ZolbbsComments.COMMENT_URL.format(field=field,boardid=boardid, bookid=bookid, page=page)
                     self.storeurl(comment_url, params.originalurl, ZolbbsComments.STEP_2, {'page': page})

            elif params.step == ZolbbsComments.STEP_2:
                # Step2: 得到所有评论，抽取评论
                self.geturlcomments(params)
            else:
                Logger.getlogging().error('proparam.step == {step}'.format(step = params.step))

        except Exception,e:
            traceback.print_exc()

    ##############################################################################################
    # @functions：geturlcomments
    # @param： 共通模块传入的参数（对象url, 原始url, 当前step数，自定义参数）
    # @return：none
    # @author：QW_Liang
    # @date：2017/9/16
    # @note：抽出的共通方法，为step1和step2调用
    ##############################################################################################
    def geturlcomments(self, params):
        xparser = XPathUtility(params.content)
        # 取回所有评论
        page = params.customized['page']
        if page == 1:
            commentstimes = xparser.getcomments('//table[position()>1]/tbody/tr/td/span[1]')
            commentscontents = xparser.getcomments('//table[position()>1]/tbody/tr[2]/td[@class="post-main"]')
            commentsnicks = xparser.getcomments('//*[@class="name"]/a')
        else:
            commentstimes = xparser.getcomments('//table/tbody/tr/td/span[1]')
            commentscontents = xparser.getcomments('//table/tbody/tr[2]/td[@class="post-main"]')
            commentsnicks = xparser.getcomments('//*[@class="name"]/a')

        # 设置实际的评论量
        for index in range(0, len(commentscontents), 1):
            curtime = TimeUtility.getuniformtime(commentstimes[index][4:])
            # 提取评论内容
            content = commentscontents[index].strip()
            nick = commentsnicks[index].strip()
            if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                CMTStorage.storecmt(params.originalurl, content, curtime, nick)

