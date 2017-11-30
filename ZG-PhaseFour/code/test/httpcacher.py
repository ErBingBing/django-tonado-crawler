# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import bsddb
import json

from configuration import constant
from configuration.constant import CHARSET_UTF8, CHARSET_DEFAULT, CHARSET_GB2312, CHARSET_GBK
from log.spiderlog import Logger
from utility.common import Common
from utility.httputil import HttpUtility
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility
import sys
import traceback
import codecs
import binascii

class HttpCacher:
    __instance = None

    def __init__(self):
        self.file = './data/httpcacher.db'
        self.urlmap = {}
        pass

    @staticmethod
    def getinstance():
        if HttpCacher.__instance is None:
            HttpCacher.__instance = HttpCacher()
        return HttpCacher.__instance

    @staticmethod
    def getcontent(url, method):
        return HttpCacher.getinstance().__getcontent(url, method)

    def __getcontent(self, url, method):
        database = bsddb.btopen(self.file, 'c')
        if database.has_key(Common.md5(url)):
            content = Common.urldec(database[Common.md5(url)]).decode(CHARSET_DEFAULT)
            database.close()
            return content
        if method == constant.REQUEST_TYPE_POST:
            js = json.loads(url)
            content = HttpUtility().post(js['url'], js['data'])
        elif method == constant.REQUEST_TYPE_WEBKIT:
            content = HttpUtility().wget(url)
        elif method == constant.REQUEST_TYPE_IMG:
            content = HttpUtility().get(url)
            content = binascii.b2a_hex(content)
        else:
            content = HttpUtility().get(url)
        if content is None:
            database.close()
            return None
        charset = RegexUtility().getid('charset', content)
        unic = Common.trydecode(content, charset)
        utf8str = unic.encode(CHARSET_UTF8)
        charset = CHARSET_UTF8
        self.urlmap[Common.md5(url)] = unic
        # content = content.encode('utf8')
        line = {"md5": Common.md5(url), "charset": charset, "html": Common.urlenc(utf8str), "url": Common.urlenc(url)}
        if len(utf8str) > 2000:
            database = bsddb.btopen(self.file, 'c')
            database[Common.md5(url)] = Common.urlenc(utf8str)
            database.close()
            # FileUtility.writeline(self.file, json.dumps(line))
        return utf8str.decode(CHARSET_UTF8)

    def trydecode(self, content, charset):
        try:
            return unicode(content, charset)
        except:
            return None

import os
import urllib
if __name__ == '__main__':
    os.chdir('..')

    print HttpCacher.getcontent('http://n.sinaimg.cn/news/crawl/20170622/eRkw-fyhneak8956843.jpg', constant.REQUEST_TYPE_IMG)

    #print urllib.unquote('http%3A%2F%2Fnews.sina.com.cn%2Fc%2Fnd%2F2016-10-09%2Fdoc-ifxwrhpm2691877.shtml')
    #info = Common.urldec(HttpCacher.getinstance().getcontent(r'http://news.163.com/16/1008/12/C2RUCHV7000146BE.html'))
    #print info
    # str = '老王 /+'
    # str = str.decode('utf8').encode('gbk')
    # str =  urllib.quote(str)
    # print str
    # str = urllib.unquote(str)
    # str = str.decode('gbk')
    # print str
    # print urllib.unquote('http%3A%2F%2Fnews.163.com%2F16%2F1008%2F12%2FC2RUCHV7000146BE.html')
    # print urllib.quote(u'比节后连上7天班更绝望的是明年国庆中秋重合了'.encode('gbk'))