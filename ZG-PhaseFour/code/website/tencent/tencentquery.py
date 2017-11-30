# -*- coding: utf-8 -*-
################################################################################################################
# @file: tencentquery.py
# @author: JiangSiwei
# @date:  2016/11/22
# @version: Ver0.0.0.100
# @note: 
################################################################################################################

from website.common.s2query import SiteS2Query
import re
from website.tencent.tvtencentquery import TvtencentQuery
from website.tencent.actencentquery import ActencentQuery
from website.tencent.ebooktencentquery import EbooktencentQuery
from website.common.bbss2postquery import BBSS2PostQuery 
from website.tencent.newstencentquery import Newstencent

################################################################################################################
# @class：tencentquery
# @author：JiangSiwei
# @date：2016/11/22
# @note：
################################################################################################################
class TencentS2Query(SiteS2Query):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SohuS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://v.qq.com'
        # 当前类还没初始化结束，传给其他类的self会有问题，因此对于要传递self的类都不能在init初始化
        self.tvtencent = None
        self.actencent = None   
        self.ebooktencent = None 
        self.postqqbooktencent= None
        self.newstencent = None
    ################################################################################################################
    # @functions：createobject
    # @param： none
    # @return：none
    # @note：创建对象实例
    ################################################################################################################        
    def createobject(self):
        if self.tvtencent is None:
            self.tvtencent = TvtencentQuery(self)
        if self.actencent is None:
            self.actencent = ActencentQuery(self)
        if self.ebooktencent is None:
            self.ebooktencent = EbooktencentQuery(self)
        if self.postqqbooktencent is None:
            self.postqqbooktencent = BBSS2PostQuery('http://bbs.book.qq.com/search.php?mod=forum', self)
        if self.newstencent is None:
            self.newstencent = Newstencent(self)

    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query
    ################################################################################################################
    def query(self, info):
        self.createobject()
        self.tvtencent.query(info)
        self.actencent.query(info)
        self.ebooktencent.query(info)
        self.postqqbooktencent.query(info)
        self.newstencent.query(info)
   
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################    
    #----------------------------------------------------------------------
    def  process(self,params):
        """"""
        # 初始化内部子类对象
        self.createobject()
        if re.search('http[s]{0,1}://v\.qq\.com.*', params.originalurl):
            self.tvtencent.process(params)
        if re.search('http[s]{0,1}://ac\.qq\.com.*', params.originalurl):
            self.actencent.process(params)
        if re.search('http[s]{0,1}://ebook\.qq\.com.*', params.originalurl):
            self.ebooktencent.process(params)
        if re.search('http[s]{0,1}://bbs.*',params.originalurl):
            self.postqqbooktencent.process(params)
        if re.search('http[s]{0,1}://news\.sogou\.com.*',params.originalurl):
            self.newstencent.process(params)
        
        
        
        
