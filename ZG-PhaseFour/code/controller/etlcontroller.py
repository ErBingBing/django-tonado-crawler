# -*- coding: utf-8 -*-
################################################################################################################
# @file: diffcontroller.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import codecs
import json
import zlib
import os
import urllib
import re
from lxml import etree
from configuration import constant
from configuration.constant import SPIDER_CHANNEL_S2, SPIDER_CHANNEL_S1, REQUEST_TYPE_WEBKIT
from configuration.environment.configure import SpiderConfigure
from controller.sitefactory import SiteFactory
from dao.sqldao import SQLDAO
from log.spiderlog import Logger
from storage.newsstorage import NewsStorage, PageBasicInfo
from storage.querystorage import QueryStorage 
from storage.storage import Storage
from storage.urlfilemanager import URLFileManager
from storage.urlmanager import URLManager, URLContext
from utility import const
from utility.common import Common
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from website.common.s2query import SiteS2Query
from website.common.site import ProcessParam
from utility.httputil import HttpUtility

################################################################################################################
# @class：ETLController
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class ETLController:
    LOCALMACHINEFLAG = SpiderConfigure.getinstance().localmachineflag()    
    
    REFER_URLS_PATTERN = [r'http[s]{0,1}://www.baidu.com/link\?url=.*']
    TIEBA_URL_PATTERN = [ constant.TIEBA_URL_PATTERN1, constant.TIEBA_URL_PATTERN12,
                          constant.TIEBA_URL_PATTERN2, constant.TIEBA_URL_PATTERN22]    
   
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.factory = SiteFactory()
        self.conf = SpiderConfigure.getinstance()
        self.urlbackuppath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                       const.SPIDER_URL_BACKUP_PATH) + TimeUtility.getcurrentdate()
        self.period = int(SpiderConfigure.getinstance().getlastdays())
 
    ################################################################################################################
    # @functions：s1process
    # @param： 从下载平台得到的json文件
    # @return：none
    # @note：执行S1，从网页中提取信息
    ################################################################################################################
    def processfile(self, jsonfile):
        if not self.preprocess(jsonfile):
            return
        method = self.requesttype(jsonfile)
        urls = self.backupfile(jsonfile)
        context = URLFileManager.getinstance().geturlfilecontext(FileUtility.getfilename(jsonfile))
        with open(jsonfile, 'r') as fp:
            lines = fp.readlines()
        for line in lines:
            param = self.analysis(line, method)
            if param is None:
                continue
            url = param.url
            if context.retry >= 2:
                param.lastretry = True
            if method == constant.REQUEST_TYPE_POST:
                url = json.dumps({'url': param.url, 'data': param.data})
            info = None
            if URLManager.getinstance().exist(url):
                info = URLManager.getinstance().geturlcontext(url)
                param.originalurl = info.originalurl
                param.step = info.step
                param.type = info.type
                param.customized = info.customized
            else:
                param.originalurl = param.url
                param.type = URLContext.S1_MAIN_BODY
            if SiteS2Query.REFER_URL in param.customized:
                site = self.factory.getsite(param.customized[SiteS2Query.REFER_URL])
            else:
                site = self.factory.getsite(param.originalurl)
            res = site.process(param)
            if not res:
                if info:
                    URLManager.getinstance().seturlcontext(param.url, info)
            else:
                if url in urls:
                    urls[url] -= 1
                    if urls[url] == 0:
                        urls.pop(url)
        # upload failed urls
        if urls:
            self.retrydownload(jsonfile, urls)

    def requesttype(self, filename):
        method = constant.REQUEST_TYPE_COMMON
        if constant.POST_FILE_SUFFIX in filename:
            method = constant.REQUEST_TYPE_POST
        elif constant.WEBKIT_FILE_SUFFIX in filename:
            method = constant.REQUEST_TYPE_WEBKIT
        elif constant.IMG_FILE_SUFFIX in filename:
            method = constant.REQUEST_TYPE_IMG
        return method

    ################################################################################################################
    # @functions：backupfile
    # @jsonfile： 返回的json文件
    # @return：源文件的所有URL
    # @note：读取源文件的所有URL
    ################################################################################################################
    def backupfile(self, jsonfile):
        urlmap = {}
        if 'split' in jsonfile:
            return urlmap
        bkfile = self.urlbackuppath + '/' + FileUtility.getfilename(jsonfile).split('.')[0]
        if FileUtility.exists(bkfile):
            with open(bkfile, 'r') as bkfh:
                for line in bkfh.readlines():
                    line = line.strip()
                    if line in urlmap:
                        urlmap[line] += 1
                    else:
                        urlmap[line] = 1
        return urlmap

    ################################################################################################################
    # @functions：retrydownload
    # @jsonfile： 返回的json文件
    # @urlset： 下载出错的URL
    # @return：none
    # @note：重传下载出错的URL
    ################################################################################################################
    def retrydownload(self, jsonfile, urlset):
        Logger.getlogging().warning('upload failed urls {num}'.format(num=len(urlset)))
        context = URLFileManager.getinstance().geturlfilecontext(FileUtility.getfilename(jsonfile))
        if context.retry >= 2:
            Logger.getlogging().error('do not upload for failed again')
            for key in urlset.keys():
                Logger.getlogging().error('download {url} failed'.format(url=key))
        else:
            urls = []
            for key in urlset.keys():
                Logger.getlogging().warning('retry download {url}'.format(url=key))
                for i in range(0, urlset[key]):
                    urls.append(key)
            newurlfile = URLFileManager.getinstance().generateurlfilepath(context.retry + 1)
            Logger.getlogging().warning('Retry download URL {file}'.format(file=newurlfile))
            if constant.POST_FILE_SUFFIX in jsonfile:
                URLManager.getinstance().storeurls(urls, constant.REQUEST_TYPE_POST)
            elif constant.WEBKIT_FILE_SUFFIX in jsonfile:
                URLManager.getinstance().storeurls(urls, constant.REQUEST_TYPE_WEBKIT)
            else:
                URLManager.getinstance().storeurls(urls, constant.REQUEST_TYPE_COMMON)

    ################################################################################################################
    # @functions：preprocess
    # @param： 下载的文件名
    # @return：none
    # @note：从文件名中提取执行信息
    ################################################################################################################
    def preprocess(self, filepath):
        result = False
        context = URLFileManager.getinstance().geturlfilecontext(FileUtility.getfilename(filepath))
        if context:
            self.conf.setchannel(context.channel)
            if context.channel == SPIDER_CHANNEL_S2:
                self.conf.setquery(context.query)
            else:
                self.conf.setquery('')
            URLFileManager.getinstance().generateurlfilepath()
            result = True
        return result

    ################################################################################################################
    # @functions：analysis
    # @param： json文件中的一行
    # @return：返回json中的数据
    # @note：解析json数据
    ################################################################################################################
    def analysis(self, line, method):
        try:
            js = json.loads(line)
            param = ProcessParam()
            param.crawler_time = TimeUtility.getuniformtime(js['crawler_time'])
            param.url = Common.urldec(js['foundin'])
            param.content = js['html']
            if method == constant.REQUEST_TYPE_POST:
                param.data = js['data']
            if js['html'][:3] == constant.GZIP_CODE:
                param.content = zlib.decompress(param.content, 16 + zlib.MAX_WBITS)
            # decode
            content = Common.urldec(param.content)
            charset = RegexUtility.getid('charset', content)
            content = Common.trydecode(content, charset)
            param.content = content
            if 'property' in js:
                for property in js['property']:
                    if not property.has_key('result'):
                        continue
                    if property['property_name'] == u'page_body':
                        param.page_body = Common.trydecode(Common.urldec(property['result'][0]['text']),
                                                           constant.CHARSET_GBK)
                    elif property['property_name'] == u'page_title':
                        param.page_title = Common.trydecode(Common.urldec(property['result'][0]['text']),
                                                            constant.CHARSET_GBK)
                    elif property['property_name'] == u'html_time':
                        param.html_time = TimeUtility.getuniformtime(property['result'][0]['text'])
            return param
        except:
            Logger.printexception()



    ################################################################################################################
    # @functions：copyfiles
    # @param： none
    # @return：none
    # @note：复制s1/s2输入文件
    ################################################################################################################
    def copyfiles(self):
        # s1/s2输入路径
        s1file = SpiderConfigure.getinstance().gets1file()
        s2file = SpiderConfigure.getinstance().gets2file()
        # s1/s2历史路径
        self.conf.setchannel(SPIDER_CHANNEL_S1)
        # s1tempfile = URLStorage.updaterecycle() + constant.WEBKIT_FILE_SUFFIX
        s2temppath = Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH)
        if FileUtility.exists(s1file):
            lines = 0
            firstline = True
            with open(s1file, 'r') as fp:
                rows = []
                for line in fp.readlines():
                    line = line.strip()
                    if firstline:
                        firstline = False
                        if line[:3] == codecs.BOM_UTF8:
                            Logger.getlogging().warning('Remove BOM from {file}!'.format(file=file))
                            line = line[3:]
                    if line:
                        lines += 1
                        rows.append(line)
                    if lines % constant.SPIDER_S1_MAX_LINE_PER_FILE == 0:
                        s1tempfile = URLFileManager.generateurlfilepath() + constant.WEBKIT_FILE_SUFFIX
                        FileUtility.writelines(s1tempfile, rows)
                        rows = []
                if rows:
                    s1tempfile = URLFileManager.generateurlfilepath() + constant.WEBKIT_FILE_SUFFIX
                    FileUtility.writelines(s1tempfile, rows)
                    rows = []
        if FileUtility.exists(s2file):
            FileUtility.copy(s2file, s2temppath)

    ##############################################################################################
    # @functions：referurl
    # @param：参数
    # @return：无
    # @note：百度高级搜索返回的搜索结果都是百度的域名，需要转换成真正的域名。
    ##############################################################################################
    def referurl(self, params):
        res = True
        for pattern in ETLController.REFER_URLS_PATTERN:
            if RegexUtility.match(pattern, params.url):
                html = etree.HTML(params.content)
                oriurl = html.xpath('//*[@rel="canonical"]/@href')
                if oriurl:
                    Logger.getlogging().debug('inurl:' + params.url)
                    params.url = oriurl[0]
                    params.originalurl = params.url
                    Logger.getlogging().debug('outurl:' + params.url)
                else:
                    res = False
                    Logger.getlogging().warning('nocanonical:' + params.url)
                break
        return res

    ##############################################################################################
    # @functions：updatedb
    # @param：none
    # @return：none
    # @note：备份数据库中过期的数据到cold数据库(表)中
    #FROM_UNIXTIME(unix_timestamp,format)
    ##############################################################################################
    def updatedb(self):
        #此处注释请勿删除
        #wheref = '{key1}={val1} and \
        #(({time1}!={time0} and TIMESTAMPDIFF(SECOND, now(), {time1}) > {secs}) or \
         #({time1}={time0} and TIMESTAMPDIFF(SECOND, now(), FROM_UNIXTIME({time2}, {timeformat})) > {secs}))'
        #where = wheref.format(key1=SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG, val1=ETLController.LOCALMACHINEFLAG,
                              #time0='\"'+TimeUtility.getuniformtime(0)+'\"',
                              #time1=SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE,
                              #time2=SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE,
                              #timeformat = '\"'+TimeUtility.SQLTIMEFORMAT+'\"',
                              #secs =self.period * 24*60*60
                              #)
        where = {SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG: ETLController.LOCALMACHINEFLAG} 
        results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, where)      
        colddata = []
        for result in results:
            data = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, result) 
            try:
                publishdate = data[SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE]
                createdate  = data[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE]
                if (publishdate == TimeUtility.getintformtime(0) and SQLDAO.gettime() - createdate > self.period * 24*60*60) or \
                   (publishdate != TimeUtility.getintformtime(0) and SQLDAO.gettime() - TimeUtility.getinttime(publishdate) > self.period * 24*60*60):
                    id = data[SQLDAO.SPIDER_TABLE_NEWS_ID]
                    colddata.append(result)
                    SQLDAO.getinstance().delete(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID:id})
            except:
                Logger.printexception()
                Logger.log(data[SQLDAO.SPIDER_TABLE_NEWS_URL], constant.ERRORCODE_WARNNING_OTHERS)
        if colddata:            
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_NEWS_COLD, SQLDAO.SPIDER_TABLE_NEWS_KEYS, colddata, mutli=True)
       
     
    def dumpurls(self):
        #dump本台机器query对应的urllsit, 并存储到对应的文件中
        s2file = SpiderConfigure.getinstance().gets2file()
        s2temppath = Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH) + FileUtility.getfilename(s2file)
        #querys = [''] + QueryStorage.getinstance().getlocalquerys(s2temppath, ETLController.LOCALMACHINEFLAG)
        querys = QueryStorage.getinstance().getlocalquerys(s2temppath, ETLController.LOCALMACHINEFLAG)
        for query in querys:
            Logger.getlogging().debug('Now, Starting Select url to Insert and Update for uploading location urlfile!')
            self.conf.setchannel(constant.SPIDER_CHANNEL_S2)
            self.conf.setquery(query)
            #此处注释请勿删除
            #1.转换周期内数据
            # 1.1pulishdate存在,时间为最近一周
            # 2.1publistdate为0,使用创建时间,时间为最近一周
            #wheref = '{key1}={val1} and {key2}={val2} and {createdate}!={starttime} and \
            #(({time1}!={time0} and TIMESTAMPDIFF(SECOND, now(), {time1}) <= {secs}) or \
             #({time1}={time0} and TIMESTAMPDIFF(SECOND, now(), FROM_UNIXTIME({time2}, {timeformat})) <= {secs}))'
            #where = wheref.format(key1=SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG, val1=ETLController.LOCALMACHINEFLAG,
                                  #key2=SQLDAO.SPIDER_TABLE_NEWS_QUERY, val2='\"'+query+'\"',
                                  #createdate = SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE, 
                                  #starttime = SpiderConfigure.getinstance().starttime(),
                                  #time0='\"'+TimeUtility.getuniformtime(0)+'\"',
                                  #time1=SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE,
                                  #time2=SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE,
                                  #timeformat = '\"'+TimeUtility.SQLTIMEFORMAT+'\"',
                                  #secs =self.period * 24*60*60
                                  #)
            where = {SQLDAO.SPIDER_TABLE_NEWS_QUERY:query, SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG: ETLController.LOCALMACHINEFLAG}      
            Logger.getlogging().debug('Query condition: {where}'.format(where=str(where)))
            results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, where)      
            urltemplist = []
            for result in results:
                data = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, result)      
                publishdate = data[SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE]
                createdate  = data[SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE]
                url = data[SQLDAO.SPIDER_TABLE_NEWS_URL].strip()
                if (publishdate == TimeUtility.getintformtime(0) and SQLDAO.gettime() - createdate <= self.period * 24*60*60) or \
                   (publishdate != TimeUtility.getintformtime(0) and SQLDAO.gettime() - TimeUtility.getinttime(publishdate) <= self.period * 24*60*60):
                    if url not in urltemplist:
                        urltemplist.append(url)                    
                        params = PageBasicInfo()
                        params.url = url
                        NewsStorage.seturlinfos(params)                       

            #2.抽取createdate为本次开始时间的数据
            URLFileManager.getinstance().generateurlfilepath()
            where = {SQLDAO.SPIDER_TABLE_NEWS_QUERY:query, 
                     SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG: ETLController.LOCALMACHINEFLAG,
                     SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE: SpiderConfigure.getinstance().starttime()
                     }
            results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, where)               
            urllist = []
            linecount = 0
            for result in results:
                data = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, result)
                url = data[SQLDAO.SPIDER_TABLE_NEWS_URL].strip()
                urllist.append(url)
                context = URLContext()
                context.originalurl = url
                context.type = URLContext.S1_MAIN_BODY
                context.customized[constant.SPIDER_S2_WEBSITE_TYPE] = data[SQLDAO.SPIDER_TABLE_NEWS_TYPE]
                Logger.getlogging().debug(url)
                URLManager.getinstance().storeurl(url, context, REQUEST_TYPE_WEBKIT)
                linecount += 1              

    ################################################################################################################
    # @functions：s1upload
    # @param： none
    # @return：none
    # @note：urls文件或query文件上传
    ################################################################################################################   
    def s1upload(self, sfile):
        if FileUtility.exists(sfile):
            lines = FileUtility.readlines(sfile)
            self.conf.setchannel(SPIDER_CHANNEL_S1)
            self.conf.setquery('')
            URLFileManager.getinstance().generateurlfilepath()            
            for line in lines:
                try:
                    url = line.strip()
                    params = PageBasicInfo()
                    params.url = url
                    #NewsStorage.seturlinfos(params)
                    context = URLContext()
                    context.originalurl = url
                    context.type = URLContext.S1_MAIN_BODY
                    Logger.getlogging().debug(url)
                    URLManager.getinstance().storeurl(url, context, REQUEST_TYPE_WEBKIT)
                except:
                    Logger.printexception()
                    
    ################################################################################################################
    # @functions：s1upload
    # @param： none
    # @return：none
    # @note：urls文件或query文件上传
    ################################################################################################################   
    def s2upload(self, sfile):
        if FileUtility.exists(sfile):  
            lines = FileUtility.readlines(sfile)
            for line in lines:
                try:
                    query = line.strip()
                    self.conf.setchannel(SPIDER_CHANNEL_S2)
                    self.conf.setquery(query)
                    URLFileManager.getinstance().generateurlfilepath()
                    allsite = self.factory.getall()
                    for site in allsite:
                        site.s2query(query)
                except:
                    Logger.printexception()
    ################################################################################################################
    # @functions：s3query
    # @param： 元搜的query条件
    # @return：none
    # @note：baidutieba元搜
    ################################################################################################################
    def s3upload(self, tiebafile):
        lines = FileUtility.readlines(tiebafile)
        querylist = []
        sitelist = []
        self.conf.setchannel(SPIDER_CHANNEL_S2)
        for strquery in lines:
            query=strquery.split('\t')[0].strip()
            url=strquery.split('\t')[1].strip()     
            Logger.getlogging().debug(query)
            Logger.getlogging().debug(url)
            self.conf.setquery(query)
            URLFileManager.getinstance().generateurlfilepath()
            querylist.append(query)
            site = self.factory.getsite(url)
            site.s2query(url)
            if site not in sitelist:
                sitelist.append(site)
            #SpiderReport.loadquery(querylist)
            #SpiderReport.loadsites(sitelist) 
    ################################################################################################################
    # @functions：getqueryfromdatabase
    # @param： 元搜的query条件
    # @return：none
    # @note：上传本地的query到数据库
    ################################################################################################################
    def storagequery(self):
        QueryStorage.updatedb()
        SpiderConfigure.getinstance().setchannel(SPIDER_CHANNEL_S2)
        s2file = SpiderConfigure.getinstance().gets2file()
        if FileUtility.exists(s2file):
            lines = FileUtility.readlines(s2file)
            for strquery in lines:
                QueryStorage.getinstance().storequery(strquery)
                QueryStorage.getinstance().storewaibuquery(strquery)
                
        tiebafile = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_S3_INPUT_FILE)
        if FileUtility.exists(tiebafile):
            lines = FileUtility.readlines(tiebafile)
            for strquery in lines:
                if not self.checks3query(strquery):
                    continue              
                query=strquery.split('\t')[0].strip()
                url=strquery.split('\t')[1].strip()  
                QueryStorage.getinstance().storetiebaquery(query, url)        
    ################################################################################################################
    # @functions：gets2queryfromdb
    # @param： 元搜的query条件
    # @return：none
    # @note：获取本地需要的query
    ################################################################################################################
    def getqueryfromdb(self):
        #指定s2 query输出文件路径
        s2file = SpiderConfigure.getinstance().gets2file()
        temppath = Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH) + FileUtility.getfilename(s2file)
        QueryStorage.getinstance().getlocalquerys(temppath, ETLController.LOCALMACHINEFLAG)        
        if FileUtility.exists(temppath):
            return temppath
    ################################################################################################################
    # @functions：gets2queryfromdb
    # @param： 元搜的query条件
    # @return：none
    # @note：获取baidutieba需要的query
    ################################################################################################################
    def gettiebaqueryfromdb(self):
        #指定s2 query输出文件路径
        tiebafile = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_S3_INPUT_FILE)
        temppath = Storage.getstoragelocation(const.SPIDER_TIEBA_TEMP_PATH) + FileUtility.getfilename(tiebafile)
        QueryStorage.getinstance().getlocalquerys_tieba(temppath, ETLController.LOCALMACHINEFLAG)        
        if FileUtility.exists(temppath):
            return temppath        
    ##############################################################################################
    # @functions：checks3query
    # @param：none
    # @return：none
    # @note：校验贴吧名与url是否对应
    ##############################################################################################    
    def checks3query(self, strquery):
        querys = strquery.split('\t')
        if len(querys) < 2:
            Logger.getlogging().error('S3 the Format of Inputing is Wrong!')
            return False
        query=querys[0]
        url=querys[1] 
        if not re.search('^http[s]{0,1}:.*',url):
            Logger.getlogging().error('S3 the Format of Inputing is Wrong!')
            return False 
        for pattern in ETLController.TIEBA_URL_PATTERN:
            if re.search(pattern, url):
                tempquery = re.findall(pattern, url)[0]
                if Common.urldec(tempquery) == query:
                    return True
                else:
                    Logger.getlogging().warning('S3 querykey and queryurl not Match!')
        return True

                    
    def wb_analysis(self, filepath):
        Logger.getlogging().info('Now, Start to analysis Waibu file {fl}'.format(fl=filepath))
        if '302_tencent_video' in filepath:
            type = constant.SPIDER_S2_WEBSITE_VIDEO
        else:
            type = constant.SPIDER_S2_WEBSITE_NEWS
        
        self.conf.setchannel(constant.SPIDER_CHANNEL_S2)
        lines = FileUtility.readlines(filepath)
        tempwaibustorage = {}
        for line in lines:
            try:
                line = json.loads(line)
                params = PageBasicInfo()
                params.query = line['query']
                params.url = line['url']
                params.title = Common.strfilter(line['title'])
                params.body = Common.strfilter(line['body'])
                params.pubtime = line['pubtime']
                clicknum = line.get('clicknum',0)
                if clicknum:
                    params.clicknum = int(clicknum)
                params.type = type
                if params.query not in URLManager.waibustorage:
                    URLManager.waibustorage[params.query] = []
                if params.query not in tempwaibustorage:
                    tempwaibustorage[params.query] = []
                URLManager.waibustorage[params.query].append(params)
                tempwaibustorage[params.query].append(params)
            except:
                Logger.printexception()
            
        Logger.getlogging().debug('Now, Starting Select url to Insert and Update for uploading WAIBU data!')
        for query in tempwaibustorage:
            paramslist = tempwaibustorage[query]
            for params in paramslist:
                self.conf.setquery(query)   
                NewsStorage.seturlinfos(params)
                
    #----------------------------------------------------------------------
    def wb_updatedb(self):
        self.conf.setchannel(constant.SPIDER_CHANNEL_S2)
        for query in URLManager.waibustorage:
            self.conf.setquery(query) 
            paramslist = URLManager.waibustorage[query]
            for params in paramslist:
                if params.type == constant.SPIDER_S2_WEBSITE_VIDEO:
                    data = {SQLDAO.SPIDER_TABLE_NEWS_TITLE:params.title,
                            SQLDAO.SPIDER_TABLE_NEWS_BODY:params.body,
                            SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE: params.pubtime,
                            SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM: params.clicknum}
                    NewsStorage.seturlinfo(params.url, data=data)
                else:
                    data = {SQLDAO.SPIDER_TABLE_NEWS_TITLE:params.title,
                            SQLDAO.SPIDER_TABLE_NEWS_BODY:params.body,
                            SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE: params.pubtime}                    
                    NewsStorage.seturlinfo(params.url, data=data)             
        
