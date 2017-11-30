# -*- coding: utf-8 -*-
################################################################################################################
# @file: diffcontroller.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import sys
import os
sys.path.append('\\'.join(os.getcwd().split('\\')[:-1]))
import codecs
import json
import zlib
from lxml import etree
from configuration import constant
from configuration.constant import SPIDER_CHANNEL_S2, SPIDER_CHANNEL_S1
from configuration.environment.configure import SpiderConfigure
from controller.sitefactory import SiteFactory
from dao.spiderdao import SpiderDao
from log.spiderlog import Logger
from statistics.inforeport import SpiderReport
from storage.storage import Storage
from storage.urlsstorage import URLStorage, URLCommentInfo
from utility import const
from utility.common import Common
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from website.common.s2query import SiteS2Query
from website.common.site import ProcessParam
from statistics.statistics import StatisticsManager

################################################################################################################
# @class：ETLController
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class ETLController:
    
    REFER_URLS_PATTERN = [
        r'http[s]{0,1}://www.baidu.com/link\?url=.*'
    ]

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

    ################################################################################################################
    # @functions：s1process
    # @param： 从下载平台得到的json文件
    # @return：none
    # @note：执行S1，从网页中提取信息
    ################################################################################################################
    def processfile(self, jsonfile):
        if not self.preprocess(jsonfile):
            return
        post = (constant.POST_FILE_SUFFIX in jsonfile)
        urls = self.backupfile(jsonfile)
        context = URLStorage.getfilecontext(FileUtility.getfilename(jsonfile))
        with open(jsonfile, 'r') as fp:
            lines = fp.readlines()
        for line in lines:
            param = self.analysis(line, post)
            if param is None:
                continue
            url = param.url
            if context.retry >= 2:
                param.lastretry = True
            if post:
                url = json.dumps({'url': param.url, 'data': param.data})
            else:
                Logger.getlogging().warning(url)
            info = None
            if URLStorage.hasurl(url):
                info = URLStorage.geturlcontext(url)
                param.originalurl = info.originalurl
                param.step = info.step
                param.customized = info.customized
            else:
                param.originalurl = param.url
            res = True
            if SiteS2Query.REFER_URL in param.customized:
                site = self.factory.getsite(param.customized[SiteS2Query.REFER_URL])
                res = site.process(param)
            else:
                site = self.factory.getsite(param.originalurl)
                res = site.process(param)
            if not res:
                if info:
                    URLStorage.seturlcontext(param.url, info)
            else:
                if url in urls:
                    urls[url] -= 1
                    if urls[url] == 0:
                        urls.pop(url)
        # upload failed urls
        if urls:
            self.retrydownload(jsonfile, urls)

    ################################################################################################################
    # @functions：backupfile
    # @jsonfile： 返回的json文件
    # @return：源文件的所有URL
    # @note：读取源文件的所有URL
    ################################################################################################################
    def backupfile(self, jsonfile):
        urlmap = {}
        splitkey = '.'
        if '_split' in jsonfile:
            splitkey = '_split'
        bkfile = self.urlbackuppath + '/' + FileUtility.getfilename(jsonfile).split(splitkey)[0]
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
        context = URLStorage.getfilecontext(FileUtility.getfilename(jsonfile))
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
            StatisticsManager.updateall(-len(urls))
            URLStorage.updaterecycle(context.retry + 1)
            if constant.POST_FILE_SUFFIX in jsonfile:
                URLStorage.storeurls(urls, constant.REQUEST_TYPE_POST)
            elif constant.WEBKIT_FILE_SUFFIX in jsonfile:
                URLStorage.storeurls(urls, constant.REQUEST_TYPE_WEBKIT)
            else:
                URLStorage.storeurls(urls, constant.REQUEST_TYPE_COMMON)

    ################################################################################################################
    # @functions：preprocess
    # @param： 下载的文件名
    # @return：none
    # @note：从文件名中提取执行信息
    ################################################################################################################
    def preprocess(self, filepath):
        result = False
        context = URLStorage.getfilecontext(FileUtility.getfilename(filepath))
        if context:
            self.conf.setchannel(context.channel)
            if context.channel == SPIDER_CHANNEL_S2:
                self.conf.setquery(context.query)
            else:
                self.conf.setquery('')
            URLStorage.updaterecycle()
            result = True
        return result

    ################################################################################################################
    # @functions：analysis
    # @param： json文件中的一行
    # @return：返回json中的数据
    # @note：解析json数据
    ################################################################################################################
    def analysis(self, line, post=False):
        param = ProcessParam()
        js = json.loads(line)
        param.crawler_time = TimeUtility.getuniformtime2(js['crawler_time'])
        param.url = Common.urldec(js['foundin'])
        param.content = js['html']
        if post:
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
                    param.html_time = TimeUtility.getuniformtime2(property['result'][0]['text'])
        return param

    ################################################################################################################
    # @functions：s2query
    # @param： 元搜的query条件
    # @return：none
    # @note：S2元搜
    ################################################################################################################
    def s2query(self):
        self.conf.setchannel(SPIDER_CHANNEL_S2)
        s2file = SpiderConfigure.getinstance().gets2file()
        file = FileUtility.getfilename(s2file)
        s2temppath = Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH) + file
        if FileUtility.exists(s2temppath):
            with open(s2temppath, 'r') as fp:
                querylist = []
                firstline = True
                for strquery in fp.readlines():
                    if firstline:
                        firstline = False
                        if strquery[:3] == codecs.BOM_UTF8:
                            Logger.getlogging().warning('Remove BOM from {file}!'.format(file=file))
                            strquery = strquery[3:]
                    strquery = Common.strip(strquery)
                    if not strquery:
                        continue
                    Logger.getlogging().info('S2 {query} start...'.format(query=strquery))
                    self.conf.setquery(strquery)
                    URLStorage.updaterecycle()
                    querylist.append(strquery)
                    for site in self.factory.getall():
                        site.s2query(strquery.replace('&', ' '))
                sitelist = []
                for site in self.factory.getall():
                    if site.exists2():
                        sitelist.append(site)
                SpiderReport.loadquery(querylist)
                SpiderReport.loadsites(sitelist)

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
        s1tempfile = URLStorage.updaterecycle() + constant.WEBKIT_FILE_SUFFIX
        s2temppath = Storage.getstoragelocation(const.SPIDER_QUERY_TEMP_PATH)
        if FileUtility.exists(s1file):
            lines = 0
            firstline = True
            with open(s1file, 'r') as fp:
                for line in fp.readlines():
                    line = line.strip()
                    if firstline:
                        firstline = False
                        if line[:3] == codecs.BOM_UTF8:
                            Logger.getlogging().warning('Remove BOM from {file}!'.format(file=file))
                            line = line[3:]
                    if line:
                        lines += 1
                        SpiderReport.puts1url(line)
            if lines > 0:
                FileUtility.copy(s1file, s1tempfile)
                SpiderReport.update(SPIDER_CHANNEL_S1, '', SpiderReport.URL_UPLOAD, lines)
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
    # @note：删除数据库中过期的数据
    ##############################################################################################
    def updatedb(self):
        items = SpiderDao().getall()
        if not items:
            return
        validdate = TimeUtility.getuniformdatebefore(SpiderConfigure.getinstance().getvalidperiod())
        removelist = []
        for key in items.keys():
            info = URLCommentInfo.fromstring(items[key])
            if info.timestamp < validdate:
                Logger.getlogging().debug(items[key])
                removelist.append(key)
        SpiderDao().remove(removelist)
        

import urllib
import os
import json
import re

def trydecode(string):
    #string = str(string)
    code = ['utf-8','gbk']
    for cd in code:
        try:
            string = string.decode(cd)
        except:
            #print 'no match '+cd
            pass
    return string

def write(line,file):
    fp = open(file,'w')
    line = trydecode(line).encode('utf-8')
    fp.write(line)
    fp.close()
def getfilelist(filepath,filelist=[]):
    if not os.path.exists(filepath):
        print 'no filepath'
        return 
    for s in os.listdir(filepath):
        if re.search('\d{3}_\w+_\d+.*\.json',s):
            filelist.append(os.path.join(filepath,s))
    return filelist
def solve(file, dirpath):
    with open(file, 'r') as fp:
        lines = fp.readlines()
    for line in lines:
        jsondata = json.loads(line)
        html = jsondata['html']
        url = jsondata['foundin']
        content = urllib.unquote(html)
        print content
        content = trydecode(content)
        print content
        print urllib.unquote(url)
        filepath = os.path.join(dirfile+url)
        write(content, filepath+'.html')
def main(srcfile, dirfile):
    filelist = getfilelist(srcfile,[])
    for fl in filelist:
        solve(fl, dirfile)
#if __name__ == '__main__':
        #srcfile = r'F:\waibao'
        #dirfile = srcfile+'\\temp'    
        #main(srcfile, dirfile)

def analysis(line):
    param = ProcessParam()
    js = json.loads(line)
  
    param.url = js['foundin']
    param.content = js['html']
    if js['html'][:3] == constant.GZIP_CODE:
        param.content = zlib.decompress(param.content, 16 + zlib.MAX_WBITS)
    # decode
    content = Common.urldec(param.content)
    charset = RegexUtility.getid('charset', content)
    content = Common.trydecode(content, charset)
    param.content = content
    return param

    
if __name__ == '__main__':
    srcfile = r'F:\waibao\mk'
    dirfile = srcfile   
    filelist = getfilelist(srcfile,[])
    for fl in filelist:
        with open(fl,'r') as fp:
            lines = fp.readlines()
        i = 0
        for line in lines:
            params = analysis(line)
            i += 1
            filename = params.url[:40]+'_{i}.html'.format(i=i)
            filepath = os.path.join(dirfile, filename)
            content = params.content
            print urllib.unquote(params.url)
            print filename
            write(content, filepath)            

        

    
