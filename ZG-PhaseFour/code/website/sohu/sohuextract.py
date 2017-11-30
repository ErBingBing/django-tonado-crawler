## -*- coding: utf-8 -*-
#################################################################################################################
## @file: sohuextract.py
## @author: Ninghz
## @date:  2017/6/20
## @version: Ver0.0.0.100

#################################################################################################################
#from website.common.s3extract import SiteS3Extract
#from utility.regexutil import RegexUtility


#################################################################################################################
## @class：SohuS3Extract
## @author：Ninghz
## @date：2017/6/20
## @note：
#################################################################################################################
#class SohuS3Extract(SiteS3Extract):

    #################################################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @note：SohuS3Extract，初始化内部变量
    #################################################################################################################
    #def __init__(self):
        #self.r = RegexUtility()
        ## 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        #SiteS3Extract.__init__(self)

    #################################################################################################################
    ## @functions：process
    ## @params： see WebSite.process
    ## @return：none
    ## @note：SohuS3Extract， process S3 extract result，一般为首页的URL列表
    #################################################################################################################
    #def process(self, params):
        ## 存储格式化后的网页url集合
        #urlList = []
        #html = params.content
        ## 取得url中含有.sohu.com的新闻网页
        #urls = self.r.parse('([http:]*//(news|www|sports|cbachina.sports)\.sohu\.com[^\s]*\d[^\s]*f=index[^\s"]*)', html)
        ## 将urls中非http:开头的url补齐,并去掉后缀的网页排序内容[?_f=index,yulenews_0_2]
        #if len(urls) > 0:
            #for url in urls:
                #url = str(url[0])
                ## 补齐http前缀
                #if url.startswith('//'):
                    #url = 'http:' + url
                ## 去掉url后缀[?_f=index,yulenews_0_2]
                #if url.find('?') != -1:
                    #url = url[0:url.find('?')]
                #if self.r.match('[^\s]*(\d\.shtml$|\d$)', url) and url.find('cfacup') == -1 and url.find('subject') == -1:
                    #urlList.append(url)
            #self.__storeurllist__(urlList)
