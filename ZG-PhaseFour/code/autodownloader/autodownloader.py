# coding=utf-8
#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())

import time
import json
import os
import sys
import urllib
import urllib2
import cookielib
import re
import zlib
from utility.regexutil import RegexUtility
from configuration import constant
from selenium import webdriver
from log.spiderlog import Logger
from utility.fileutil import FileUtility
from utility.common import Common
from utility import const
from configuration.environment.configure import SpiderConfigure
from utility.timeutility import TimeUtility
################################################################################################################
# @class：phantomjs
# @author：Jiangsiwei
# @date：2017/06/13 13:00
# @note：使用phantomjs获取网页内容
################################################################################################################
class WebKit:
    
    def __init__(self):
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            phantomjspath = "./autodownloader/phantomjs/bin/phantomjs.exe"
        else:
            phantomjspath = "./autodownloader/phantomjs/bin/phantomjs"
        self.driver = webdriver.PhantomJS(executable_path=phantomjspath, service_log_path='./logs/phantomjs.log')
        #self.driver = webdriver.Firefox(executable_path="C:/Program Files/Mozilla Firefox/firefox.exe")
        self.waitsec = 5
        self.driver.set_page_load_timeout(15)  
        self.driver.set_script_timeout(15)            
    #----------------------------------------------------------------------
    def get(self, url):
        saveJson = {}
        try:
            Logger.getlogging().debug('Downloading: {url}'.format(url=url))
            self.driver.get(url)
            time.sleep(self.waitsec)
            html = self.driver.page_source
            Logger.getlogging().debug('Request Sucessed: {url}'.format(url=url))
        except:
            Logger.getlogging().error('Request   Failed: {url}'.format(url=url))
            Logger.printexception()
            return None
        charset = RegexUtility.getid('charset', html)
        html = Common.trydecode(html, charset)
        saveJson['foundin'] = Common.urlenc(url)
        saveJson['html'] = Common.urlenc(html.encode(constant.CHARSET_UTF8))
        saveJson['crawler_time'] = int(time.time())
        jsonStr = json.dumps(saveJson)
        return jsonStr    
    def close(self):
        self.driver.close()
    #----------------------------------------------------------------------
    def quit(self):
        self.driver.quit()
        
        
class Get:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.timeout = 2
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            proxy_handler = urllib2.ProxyHandler({'http': 'dev-proxy.oa.com:8080'})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)        
        self.headers = {
            'Content-Type':'application/x-www-form-urlencoded',
            'Cookie':'Hjj6_2132_saltkey=hh8pqWHQ; Hjj6_2132_lastvisit=1488171801; Hjj6_2132_lastact=1488445920%09search.php%09forum; Hjj6_2132_sid=RjHhtH; Hm_lvt_dcb5060fba0123ff56d253331f28db6a=1488175469,1488445986; Hm_lpvt_dcb5060fba0123ff56d253331f28db6a=1488445989',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch'
        }
    ################################################################################################################
    # @functions：get
    # @param： url
    # @return：url内容
    # @note：根据URL获取文件内容，不能返回动态数据，只能处理200情况，其他情况返回空
    ################################################################################################################
    def get(self, url):
        saveJson = {}
        try:
            Logger.getlogging().debug('Downloading: {url}'.format(url=url))
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request, timeout=self.timeout)
            code = response.getcode()
            info = response.info()
            # 判断返回的code，如果不是200，则返回空
            if code == 200:
                html = response.read()
                if (("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")):
                    html = zlib.decompress(html, 16 + zlib.MAX_WBITS);
                Logger.getlogging().debug('Request Sucessed: {url}'.format(url=url))
            else:
                Logger.getlogging().error('open {url} error, code = {code}'.format(url=url, code=code))
                Logger.getlogging().error('Request Failed: {url}'.format(url=url))
                return None
        except:
            Logger.getlogging().error('Request   Failed: {url}'.format(url=url))
            Logger.printexception()
            return None
        charset = RegexUtility.getid('charset', html)
        html = Common.trydecode(html, charset)
        saveJson['foundin'] = Common.urlenc(url)
        saveJson['html'] = Common.urlenc(html.encode(constant.CHARSET_UTF8))
        saveJson['crawler_time'] = int(time.time())
        jsonStr = json.dumps(saveJson)
        return jsonStr     
    
class Post:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.timeout = 2
        self.sitecookie = {}
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            proxy_handler = urllib2.ProxyHandler({'http': 'dev-proxy.oa.com:8080'})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)      
            self.headers = {
                'Content-Type':'application/x-www-form-urlencoded',
                'Cookie':'Hjj6_2132_saltkey=hh8pqWHQ; Hjj6_2132_lastvisit=1488171801; Hjj6_2132_lastact=1488445920%09search.php%09forum; Hjj6_2132_sid=RjHhtH; Hm_lvt_dcb5060fba0123ff56d253331f28db6a=1488175469,1488445986; Hm_lpvt_dcb5060fba0123ff56d253331f28db6a=1488445989',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, sdch'
            }        
        else:
            self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            }
    ################################################################################################################
    # @functions：get
    # @param： url
    # @return：url内容
    # @note：根据URL获取文件内容，不能返回动态数据，只能处理200情况，其他情况返回空
    ################################################################################################################
    def post(self, url, data, cookie=None):
        saveJson = {}
        try:
            Logger.getlogging().info(url)
            Logger.getlogging().info(str(data))
            if cookie:
                self.headers['Cookie'] = cookie
            request = urllib2.Request(url, data, headers=self.headers)
            response = urllib2.urlopen(request, timeout=self.timeout)
            code = response.getcode()
            info = response.info()
            # 判断返回的code，如果不是200，则返回空
            if code == 200:
                html = response.read()
                if (("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")):
                    html = zlib.decompress(html, 16 + zlib.MAX_WBITS);
                Logger.getlogging().debug('Request Sucessed: {url}'.format(url=url))
            else:
                Logger.getlogging().error('open {url} error, code = {code}'.format(url=url, code=code))
                Logger.getlogging().error('Request Failed: {url}'.format(url=url))
                return None
        except:
            Logger.getlogging().error('Request   Failed: {url}'.format(url=url))
            Logger.printexception()
            return None  
        charset = RegexUtility.getid('charset', html)
        html = Common.trydecode(html, charset)
        saveJson['foundin'] = Common.urlenc(url)
        saveJson['html'] = Common.urlenc(html.encode(constant.CHARSET_UTF8))
        saveJson['data'] = data
        saveJson['crawler_time'] = str(int(time.time()))
        jsonStr = json.dumps(saveJson)
        return jsonStr 
    
    ################################################################################################################
    # @functions：createCookie
    # @author：JiangSiwei
    # @date：none
    # @note：创建一个cookie
    ################################################################################################################
    def createCookie(self, url):
        site = Post.getdomain(url)
        if site in self.sitecookie:
            return self.sitecookie[site]
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(handler)
        # 创建请求
        res = opener.open(url,timeout=self.timeout)
        strCookie = ''
        for item in cookie:
            strCookie = strCookie + item.name + '=' + item.value + ';'
        self.sitecookie[site] = strCookie
        return strCookie
       
    #----------------------------------------------------------------------
    @staticmethod
    def getdomain(url):
        pattern = '^https?://.*\.(\w+)\.(com|cn|org|net|me)'
        if re.search(pattern, url):
            site = re.findall(pattern, url)[0][0]
        else:
            site = 'others'
        return site
        
#----------------------------------------------------------------------
def downWebkit(urlfilepath, writeTmpfile, second=1):
    webkit = WebKit()
    try:
        lines = FileUtility.readlines(urlfilepath)
        for line in lines:
            try:
                jsonstr = webkit.get(line.strip())
                if not jsonstr:
                    Logger.getlogging().debug('Download URL failed: {url}'.format(url=line.strip()))
                    continue                
                with open(writeTmpfile,'a+') as filetemp:
                    filetemp.write(jsonstr+'\n')
                time.sleep(second)
            except:                
                Logger.printexception()
    except:
        Logger.printexception()
    finally:
        #webkit.close()
        webkit.quit()
        
#----------------------------------------------------------------------
def downGet(urlfilepath, writeTmpfile, second=2):
    get = Get()
    try:
        lines = FileUtility.readlines(urlfilepath)
        for line in lines:
            try:   
                jsonstr = get.get(line.strip())
                if not jsonstr:
                    Logger.getlogging().debug('Download URL failed: {url}'.format(url=line.strip()))
                    continue
                with open(writeTmpfile,'a+') as filetemp:
                    filetemp.write(jsonstr+'\n')
                time.sleep(second)
            except:                 
                Logger.printexception()
    except:
        Logger.printexception()
            
#----------------------------------------------------------------------
def downPost(urlfilepath, writeTmpfile, second=10):
    post = Post()
    try:
        lines = FileUtility.readlines(urlfilepath)
        lenth = len(lines)
        for line in lines:
            jsonline = json.loads(line.strip())
            try: 
                url = jsonline['url']
                data = jsonline['data']
                #cookie = post.createCookie(url)
                jsonstr = post.post(url, data, cookie=None)
                if not jsonstr:
                    Logger.getlogging().debug('Download URL failed: url:{url}\tdata:{data}'.format(url=url, data=str(data)))
                    continue                
                with open(writeTmpfile,'a+') as filetemp:
                    filetemp.write(jsonstr+'\n')
                if lenth > 1:
                    time.sleep(second)
                lenth = lenth - 1
            except:               
                Logger.printexception()
    except:
        Logger.printexception()    

#----------------------------------------------------------------------
def download(urlfilepath):
    whoami = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, const.SPIDER_LOCAL_WHOAMI)
    donepath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, whoami + constant.DOWNLOADER_DONE_PATH)
    FileUtility.mkdirs(donepath)  
    filename = os.path.basename(urlfilepath)
    writeTmpfile = os.path.join(donepath, filename+'.temp')
    writefile = os.path.join(donepath, filename + '.txt.' + str(int(time.time())) + '.done')
    if os.path.exists(writeTmpfile):
        os.remove(writeTmpfile)
    if os.path.exists(writefile):
        os.remove(writefile) 
    httpsflag = False
    if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
        readlines = FileUtility.readlines(urlfilepath)
        for line in readlines:
            if line.strip().startswith('https'):
                httpsflag = True
                break
    #创建空文件
    with open(writeTmpfile,'a+') as filetemp:
        filetemp.write('')    
    if urlfilepath.endswith(constant.WEBKIT_FILE_SUFFIX) or httpsflag:
        downWebkit(urlfilepath, writeTmpfile)
    elif urlfilepath.endswith(constant.POST_FILE_SUFFIX):
        downPost(urlfilepath, writeTmpfile)
    else:
        downGet(urlfilepath, writeTmpfile)
    if os.path.exists(writeTmpfile):
        os.rename(writeTmpfile, writefile)
        Logger.getlogging().debug('DoneFile Download Success: {f}'.format(f=writefile))
    FileUtility.remove(urlfilepath)       

    
#----------------------------------------------------------------------
def scanning():
    whoami = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, const.SPIDER_LOCAL_WHOAMI)
    scanningPath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, whoami + constant.DOWNLOADER_URL_PATH)
    donepath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, whoami + constant.DOWNLOADER_DONE_PATH)
    FileUtility.removefiles(donepath)
    backupPath = os.path.join(SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, const.DOWNLOADER_URL_BACKUP), TimeUtility.getcurrentdate())
    interval = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN, const.DOWNLOADER_INTERVAL)
    FileUtility.mkdirs(scanningPath)
    FileUtility.mkdirs(backupPath) 
    while True:
        Logger.getlogging().debug('scanning')
        flag = False
        for filename in os.listdir(scanningPath):
            try:
                urlfilepath = os.path.join(scanningPath, filename)
                backupfile  = os.path.join(backupPath, filename)
                if os.path.isfile(urlfilepath) and 'tmp' not in filename:
                    Logger.getlogging().info('Get url file:{file}'.format(file=filename))
                    FileUtility.copy(urlfilepath, backupfile)
                    download(urlfilepath)
                if not flag:
                    flag = True
            except:
                Logger.printexception()
        if not flag:
            Logger.getlogging().debug('scanning interval sleeping {interval}s'.format(interval=interval))
            time.sleep(int(interval))    


#----------------------------------------------------------------------
if __name__ == '__main__':   
    reload(sys)
    sys.setdefaultencoding('utf8')    
    scanning()
    #js = {"url": "http://bbs.17173.com/search.php?mod=forum", "data": "searchsubmit=yes&srchtxt=lol"}
    #url = js['url']
    #data = js['data']
    #Post().post(url, data)
           
           
            
    
