# -*- coding: utf-8 -*-
###################################################################################################
# @file: diffcontrollermock.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note: etlcontroller.ETLController的测试文件
###################################################################################################
import json
import zlib
from log.spiderlog import Logger
from test.httpcacher import HttpCacher
from website.common.site import ProcessParam
import controller.etlcontroller
from configuration import constant
from log.spiderlog import Logger
from website.common.site import ProcessParam
from utility.timeutility import TimeUtility 
from utility.common import Common
from utility.regexutil import RegexUtility
################################################################################################################
# @class：ETLController
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：etlcontroller.ETLController的测试类
################################################################################################################
class ETLController(controller.etlcontroller.ETLController):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        controller.etlcontroller.ETLController.__init__(self)
    #################################################################################################################
    #@functions：analysis
    #@param： json文件中的一行，为URL
    #@return：返回json中的数据
    #@note：测试环境下输入一行为一个url，根据url下载对应的网页
    #################################################################################################################
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
            return param
        except:
            line = line.replace('\n', '').strip()
            if not line or line[0] == '#':
                return
            Logger.getlogging().debug(line)
            param = ProcessParam()
            param.url = line
            if method == constant.REQUEST_TYPE_POST:
                js = json.loads(line)
                param.url = js['url']
                param.data = js['data']
            param.content = HttpCacher.getcontent(line, method)
            if param.content is None:
                return
            return param
    
    


