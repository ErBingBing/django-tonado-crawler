# coding=utf-8
################################################################################################################
# @file: httputil.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())

import json
import re
import urllib
import urllib2

from configuration import constant
from log.spiderlog import Logger
import zlib
import socket


################################################################################################################
# @class：HttpUtility
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from utility.common import Common


class HttpUtility:

    webdriver = None
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
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
        try:
            Logger.getlogging().info(url)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            code = response.getcode()
            info = response.info()
            # 判断返回的code，如果不是200，则返回空
            if code == 200:
                html = response.read()
                if (("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")):
                    html = zlib.decompress(html, 16 + zlib.MAX_WBITS);
                Logger.getlogging().debug(url)
                return html
            else:
                Logger.getlogging().error('open {url} error, code = {code}'.format(url=url, code=code))
        except:
            Logger.getlogging().error(url)
            Logger.printexception()

    def wget(self, url):
        # try:
        #     if HttpUtility.webdriver is None:
        #         if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
        #             phantomjspath = "./tools/phantomjs/bin/phantomjs.exe"
        #         else:
        #             phantomjspath = "./tools/phantomjs/bin/phantomjs"
        #         HttpUtility.webdriver = webdriver.PhantomJS(executable_path=phantomjspath,
        #                                           service_log_path='./logs/phantomjs.log')
        #     Logger.getlogging().info(url)
        #     HttpUtility.webdriver.get(url)
        #     html = HttpUtility.webdriver.page_source
        #     Logger.getlogging().debug(url)
        #     return html
        # except:
        #     Logger.getlogging().error(url)
        #     Logger.printexception()
        return self.get(url)

    ################################################################################################################
    # @functions：get
    # @param： url
    # @return：url内容
    # @note：根据URL获取文件内容，不能返回动态数据，只能处理200情况，其他情况返回空
    ################################################################################################################
    def post(self, url, data):
        try:
            Logger.getlogging().info(url)
            request = urllib2.Request(url, data, self.headers)
            response = urllib2.urlopen(request)
            code = response.getcode()
            info = response.info()
            # 判断返回的code，如果不是200，则返回空
            if code == 200:
                html = response.read()
                if (("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")):
                    html = zlib.decompress(html, 16 + zlib.MAX_WBITS);
                Logger.getlogging().debug(url)
                return html
            else:
                Logger.getlogging().error('open {url} error, code = {code}'.format(url=url, code=code))
        except:
            Logger.getlogging().error(url)
            Logger.printexception()


socket.setdefaulttimeout(60.0)

import os
import sys

if __name__ == '__main__':
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    #.chdir('..')
    # content = HttpUtility().get('http://donghua.dmzj.com/search.html?s=%E6%B5%B7%E8%B4%BC%E7%8E%8B')
    # content = HttpUtility().get('http://www.joyme.com/news/newpicture/201610/08159469.html#')
    #content = HttpUtility().get('http://n.sinaimg.cn/news/transform/20170623/EdVx-fyhneak9721617.jpg')
    #print content
    data = {"url": "https://www.huxiu.com/comment/getCommentList", "data": "object_type=1&type=2&object_id=214764"}
    print HttpUtility().get(data['url']+'?'+data['data'])