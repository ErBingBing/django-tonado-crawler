# -*- coding: utf-8 -*-
################################################################################################################
# @file: baiduquery.py
# @author: Hedian
# @date:  2016/12/02
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
from website.baidu.baidutiebaquery import BaiduTiebaS2Query
from website.baidu.baidutiebaquery2 import BaiduTiebaS2Query2
from website.common.s2query import SiteS2Query
from log.spiderlog import Logger
################################################################################################################
# @class：BaiduS2Query
# @author：Hedian
# @date：2016/12/02
# @note：
################################################################################################################
class BaiduS2Query(SiteS2Query):
    # 内部执行分支条件

    # 百度贴吧分支条件
    BAIDU_TIEBA_SEARCH_FIRST_PAGE = 'BAIDU_TIEBA_SEARCH_FIRST_PAGE'
    BAIDU_TIEBA_SEARCH_EACH_PAGE = 'BAIDU_TIEBA_SEARCH_EACH_PAGE'
    # 百度贴吧分支条件2
    BAIDU_TIEBA_SEARCH_FIRST_PAGE2 = 'BAIDU_TIEBA_SEARCH_FIRST_PAGE2'
    BAIDU_TIEBA_SEARCH_EACH_PAGE2 = 'BAIDU_TIEBA_SEARCH_EACH_PAGE2'    

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：BaiduS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        SiteS2Query.__init__(self)
        self.fakeoriginalurl = 'https://www.baidu.com'
        # 当前类还没初始化结束，传给其他类的self会有问题，因此对于要传递self的类都不能在init初始化
        self.baidutieba = None
        self.baidutieba2 = None
    ################################################################################################################
    # @functions：createobject
    # @param： none
    # @return：none
    # @note：初始化实现真正检索的类对象，需要把接口类的self传递给类
    ################################################################################################################
    def createobject(self):
        if self.baidutieba is None:
            self.baidutieba = BaiduTiebaS2Query(self)   
        if self.baidutieba2 is None:
            self.baidutieba2 = BaiduTiebaS2Query2(self) 
    ################################################################################################################
    # @functions：query
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def query(self, info):
        try:
            # 初始化内部子类对象
            self.createobject()
            # 执行百度贴吧搜索
            self.baidutieba.baidutiebasearch_step1(info)
            self.baidutieba2.baidutiebasearch_step1(info)
        except:
            Logger.printexception()
    ################################################################################################################
    # @functions：process
    # @params： see WebSite.process
    # @return：none
    # @note：SiteS2Query， process S2 query result，一般为查询到的URL列表
    ################################################################################################################
    def process(self, params):
        try:
            # 初始化内部子类对象
            self.createobject()
            if params.step == BaiduS2Query.BAIDU_TIEBA_SEARCH_FIRST_PAGE:
                self.baidutieba.baidutiebasearch_step2(params)
            elif params.step == BaiduS2Query.BAIDU_TIEBA_SEARCH_EACH_PAGE:
                self.baidutieba.baidutiebasearch_step3(params)
                
            elif params.step == BaiduS2Query.BAIDU_TIEBA_SEARCH_FIRST_PAGE2:
                self.baidutieba2.baidutiebasearch_step2(params)
            elif params.step == BaiduS2Query.BAIDU_TIEBA_SEARCH_EACH_PAGE2:
                self.baidutieba2.baidutiebasearch_step3(params)
        except:
            Logger.printexception()