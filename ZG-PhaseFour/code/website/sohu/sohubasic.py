## -*- coding: utf-8 -*-
#################################################################################################################
## @file: sohubasic.py
## @author: Ninghz
## @date:  2017/6/21
## @version: Ver0.0.0.100
## @note:
#################################################################################################################
#from website.common.s1basic import SiteS1Basic
#from dao.mongodao import MongoDAO
#from storage.newsstorage import NewsStorage
#from utility.regexutil import RegexUtility
#from utility.xpathutil import XPathUtility
#from utility.timeutility import TimeUtility
#from utility.gettimeutil import getuniformtime
#from log.spiderlog import Logger


#################################################################################################################
## @class：SohuS1Basic
## @author：Ninghz
## @date：2017/6/21
## @note：
#################################################################################################################
#class SohuS1Basic(SiteS1Basic):
    #URLPATERNKEY = 'urlpattern'
    #TITLEKEY = 'titlexpath'
    #BODYKEY = 'bodyxpath'
    #PUBTIMEKEY = 'pubtimexpath'
    #MEDIAKEY = 'medialaiyuanxpath'
    #IMAGEKEY = 'imagexpath'
    #PATTERNS = []
    #PATTERN1 = {
        #URLPATERNKEY: '^http://www\.sohu\.com/a/.*|^http://(\w+\.)?\w+\.sohu\.com/\d+/\w+\.shtml$',
        #TITLEKEY: '//h1',
        #BODYKEY: '//*[@id="contentText"]//p|//*[@class="article"]/p',
        #MEDIAKEY: '//*[@id="media_span"]//*[@itemprop="name"]|//*[@id="user-info"]/h4|//*[@class="a_source"]',
        #PUBTIMEKEY: '//*[@id="pubtime_baidu"]|//*[@id="news-time"]|//*[@class="a_time"]',
        #IMAGEKEY: '//*[@align="center"]/img/@src'}
    #PATTERNS.append(PATTERN1)

    #PATTERN2 = {
        #URLPATERNKEY: '(^http://\w+\.blog\.sohu\.com.*\.html$)',
        #TITLEKEY: '//h2/span[1]',
        #BODYKEY: '//*[@id="main-content"]',
        #MEDIAKEY: '',
        #PUBTIMEKEY: '//*[@class="date"]',
        #IMAGEKEY: ''}
    #PATTERNS.append(PATTERN2)
    ##
    ## PATTERN3 = {
    ##     URLPATERNKEY: '(^http://(\w+\.)?\w+\.sohu\.com/\d+/\w+\.shtml$)',
    ##     TITLEKEY: '//h1',
    ##     BODYKEY: '//*[@id="contentText"]|//*[@class="article"]',
    ##     MEDIAKEY: '//*[@id="media_span"]//*[@itemprop="name"]|//*[@id="media_span"]',
    ##     PUBTIMEKEY: '//*[@id="pubtime_baidu"]|//*[@class="time"]',
    ##     IMAGEKEY: ''}
    ## PATTERNS.append(PATTERN3)

    #################################################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @note：SohuS1Basic，初始化内部变量
    #################################################################################################################
    #def __init__(self):
        ## 使用该URL识别回传S2查询结果的类，推荐使用主站URL
        #SiteS1Basic.__init__(self)
        #self.r = RegexUtility()

    #################################################################################################################
    ## @functions：process
    ## @params： see WebSite.process
    ## @return：none
    ## @note：SiteS1Basic，匹配xpath，获取标题，正文，发布时间数据
    #################################################################################################################
    #def process(self, params):
        #try:
            #'''载入下载内容，使用xpath方法获取'''
            #title,body,medianame,pubtime,image='','','','',''            
            #xparser = XPathUtility(params.content)
            #for item in self.PATTERNS:
                #if self.r.match(item[self.URLPATERNKEY], params.originalurl):
                    #'''统一调用getstring2方法,处理有固定分隔符的xpath'''
                    #title = xparser.getstring2(item[self.TITLEKEY])
                    #body = xparser.getstring2(item[self.BODYKEY])
                    #medianame = xparser.getstring2(item[self.MEDIAKEY])
                    #pubtime = xparser.getstring2(item[self.PUBTIMEKEY])
                    #if item[self.IMAGEKEY]:
                        #image = xparser.xpath(item[self.IMAGEKEY])
                    #break
            #if body:
                #print body
                #body = self.filterstr(body)
            #if pubtime:
                #pubtime = getuniformtime(pubtime)
            #image = self.getimage(image, params)
            #if not title:
                #title = 'no title'
            #if not body:
                #body = 'no body'
            #if not pubtime:
                #pubtime = '1970-01-01 08:00:00'
            #if not medianame:
                #medianame = 'no name'
            #if not image:
                #image = 'no image'
            #Logger.getlogging().debug("url\t: "+params.originalurl)
            #Logger.getlogging().debug("title\t: "+title)
            #Logger.getlogging().debug("body\t: "+body)
            #Logger.getlogging().debug("medianame\t: "+medianame)
            #Logger.getlogging().debug("pubtime\t: "+pubtime)
            #Logger.getlogging().debug("image\t: "+str(image))
            #dict = {MongoDAO.SPIDER_COLLECTION_NEWS_TITLE: title,
                    #MongoDAO.SPIDER_COLLECTION_NEWS_BODY: body,
                    #MongoDAO.SPIDER_COLLECTION_NEWS_PUBLISH_DATE: pubtime,
                    #MongoDAO.SPIDER_COLLECTION_NEWS_MEDIA_NAME: medianame,
                    #MongoDAO.SPIDER_COLLECTION_NEWS_IMAGE_URL: image}
            #'''
            ##提交数据库，注意url存储的方法有2个注意区分
            ##1、seturlinfo方法是有具体变量的
            ##2、seturlinfos方法是传递数据字典的方式插入，数据字段中的字段值是各个网站自行追加参数数量，本例使用数据字段方式传值'''
            #NewsStorage.seturlinfos(params.originalurl, dict)
        #except:
            #Logger.printexception()