# -*- coding: utf-8 -*-
################################################################################################################
# @file: s2query.py
# @author: Sun Xinghua
# @date:  2017/6/14 16:21
# @version: Ver0.0.0.100
# @note:
################################################################################################################


################################################################################################################
# @class：S3HomePage
# @author：Sun Xinghua
# @date：2017/6/14 16:21
# @note：
################################################################################################################
from storage.newsstorage import NewsStorage
from lxml import etree
from utility.regexutil import RegexUtility

class SiteS3Extract:
    URLPATTERNS = ['https?://.*.s?html?']
    OTHRESPATTERNS = []
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SiteS2Query，初始化内部变量
    ################################################################################################################
    def __init__(self):
        pass
    ################################################################################################################
    # @functions：process
    # @info： query condition
    # @return：none
    # @note：SiteS2Query，S2 query
    ################################################################################################################
    def process(self, params):
        if params.originalurl.endswith('/'):
            before = '/'.join(params.originalurl.split('/')[0:-1])
        else:
            before = params.originalurl
        urllist = []
        html = etree.HTML(params.content)
        # 取得url中含有的新闻网页
        templist = html.xpath('//a/@href')
        for url in templist:
            if not url.startswith('http'):
                if url.startswith('../'):
                    new = url.split('../')[-1]
                    url = before + '/' + new
                elif url.startswith('./'):
                    new = url.split('./')[-1]
                    url = before + '/' + new    
                elif url.startswith('/'):
                    url = before + url
                else:
                    url = before + '/' + url
            #需要匹配的模式self.URLPATTERNS
            for pattern in self.URLPATTERNS:
                if self.r.search(pattern,url):
                    flag = True
                    #排除不在范围内的站点self.OTHRESPATTERNS：如果不在范围内，则flag=False
                    for other in self.OTHRESPATTERNS:
                        if self.r.search(other,url):
                            flag = False
                            break
                    if flag:
                        urllist.append(url)
                        break
        self.__storeurllist__(urllist)

    ################################################################################################################
    # @functions：setwebsite
    # @website： 主站
    # @return：none
    # @note：设置主站
    ################################################################################################################
    def setwebsite(self, website):
        self.website = website

    ################################################################################################################
    # @functions：storeurllist
    # @urllist： S2查询结果的URL列表
    # @return：none
    # @note：SiteS2Query， 保存S2查询结果的URL列表（例如视频列表）
    ################################################################################################################
    def __storeurllist__(self, urllist):
        for url in urllist:
            temp = url.strip().split('\t')
            if temp:
                url = temp[-1]
            NewsStorage.storeurl(url, True)