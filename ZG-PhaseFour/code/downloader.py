# coding=utf-8
import os
import shutil
import urllib
import urllib2
import cookielib
import json
import time

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from template.templatemanger import TemplateManager
from utility import const
from utility.common import Common
from utility.fileutil import FileUtility

import lxml.html as H

timeout = 1
################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2017/03/06 14:00
# @note：执行扫描  每次完成后10秒再次扫描
################################################################################################################
def timing():
    while True:
        Logger.getlogging().debug('scanning')
        scanning()


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2017/03/06 14:05
# @note：扫描路径下是否有文件 如果文件不是.tmp 复制文件到./gc/scanningBackups
################################################################################################################
def scanning():
    whoami = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, const.SPIDER_POST_WHOAMI)
    scanningPath = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, whoami + constant.DOWNLOADER_URL_PATH)
    backupPath = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, const.DOWNLOADER_URL_BACKUP)

    FileUtility.mkdirs(scanningPath)
    FileUtility.mkdirs(backupPath)
    flag = False
    for filename in os.listdir(scanningPath):
        fp = os.path.join(scanningPath, filename)
        backupfile = os.path.join(backupPath, filename)
        if os.path.isfile(fp) and 'tmp' not in filename:
            Logger.getlogging().info('Get url file:{file}'.format(file=filename))
            FileUtility.move(fp, backupfile)
            readFile(backupfile, filename)
        if not flag:
            flag = True
    if not flag:
        time.sleep(10)


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2017/03/06 14:15
# @note：先判断是否有写入文件和写入临时文件 如果有 先删除 再生成一个写入临时文件 读取copy的文件
################################################################################################################
def readFile(urlpath, filename):
    whoami = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, const.SPIDER_POST_WHOAMI)
    donepath = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, whoami + constant.DOWNLOADER_DONE_PATH)
    FileUtility.mkdirs(donepath)
    writeTmpfile = donepath + filename + '.tmp'
    now = str(time.time()).split('.')[0]
    writefile = donepath + filename + '.txt.' + now + '.done'
    if os.path.exists(writeTmpfile):
        os.remove(writeTmpfile)
    if os.path.exists(writefile):
        os.remove(writefile)
    Logger.getlogging().debug('post_done start:{f}'.format(f=writefile))
    with open(urlpath, 'r') as fp:
        lines = fp.readlines()
        os.mknod(writeTmpfile)
        for line in lines:
            jsonLine = json.loads(line)
            try:
                jsonStr = downPost(jsonLine)
                with open(writeTmpfile,'a+') as filetemp:
                    filetemp.write(jsonStr+'\n')
                Logger.getlogging().debug('{url}:Post request sucessed'.format(url=jsonLine['url']))
            except:
                Logger.getlogging().warning('{url}:Post request failed'.format(url=jsonLine['url']))
                Logger.printexception()
    if os.path.exists(writeTmpfile):
        os.rename(writeTmpfile, writefile)
        Logger.getlogging().debug('post_done end:{f}'.format(f=writefile))
    FileUtility.remove(urlpath)


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2017/03/06 14:20
# @note：使用post方式爬取页面并保存内容
################################################################################################################
def downPost(urlitem):
    interval = SpiderConfigure.getconfig(const.SPIDER_POST_DOMAIN, const.DOWNLOADER_INTERVAL)
    firstTime = time.time()
    urlKey = ''
    formhash = ''
    postheaders = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    
    url = urlitem['url']
    data = urlitem['data']
    thisUrlKey = TemplateManager.getdomain(url)
    if thisUrlKey == urlKey:
        now = time.time()
        timedif = now - firstTime
        print timedif
        print interval
        if timedif < float(interval):
            time.sleep(float(interval) - timedif)
        if constant.SPIDER_POST_FORMHASH_VALUE in data:
            data = data.replace(constant.SPIDER_POST_FORMHASH_VALUE, formhash)
    else:
        cookie = createCookie(url)
        postheaders['Cookie'] = cookie
        if constant.SPIDER_POST_FORMHASH_VALUE in data:
            getRequest = urllib2.urlopen(urllib2.Request(url, headers=postheaders))
            formhash = H.document_fromstring(getRequest.read()).xpath("// input[ @ name = 'formhash'] / @value")[0]
            data = data.replace(constant.SPIDER_POST_FORMHASH_VALUE, formhash)
    req = urllib2.Request(url, data, headers=postheaders)
    response = urllib2.urlopen(req,timeout=timeout)
    the_page = response.read()
    urlKey = thisUrlKey
    firstTime = time.time()
    saveJson = {}
    saveJson['html'] = Common.urlenc(the_page)
    saveJson['data'] = urlitem['data']
    saveJson['foundin'] = url
    saveJson['crawler_time'] = str(time.time()).split('.')[0]
    jsonStr = json.dumps(saveJson)
    return jsonStr    
    
################################################################################################################
# @functions：createCookie
# @author：Sun Xinghua
# @date：none
# @note：创建一个cookie
################################################################################################################
def createCookie(url):
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    # 创建请求
    res = opener.open(url,timeout=timeout)
    strCookie = ''
    for item in cookie:
        strCookie = strCookie + item.name + '=' + item.value + ';'
    return strCookie

# 入口
if __name__ == '__main__':
    timing()
