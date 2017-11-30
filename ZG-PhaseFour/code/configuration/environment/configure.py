# -*- coding: utf-8 -*-
##################################################################################################
# @file: diffcontroller.py
# @author: Sun Xinghua
# @date:  2016/11/20 10:42
# @version: Ver0.0.0.100
# @note:
##################################################################################################

from __future__ import with_statement
import ConfigParser

##################################################################################################
# @class：ConfigParser
# @author：Sun Xinghua
# @date：2016/11/20 10:42
# @note：
##################################################################################################
import time
import re
import subprocess
import traceback
from configuration import constant
from configuration.constant import SPIDER_CHANNEL_S1, SPIDER_CHANNEL_S2
from utility import const
################################################################################################################
# @file: configure.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################

################################################################################################################
# @class：SpiderConfigure
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility


class SpiderConfigure:
    CONFIG_FILE_PATH = './resources/env.ini'
    CONFIG_CHANNEL = 'channel'
    CONFIG_TYPE = 'type'
    CONFIG_QUERY = 'query'
    CONIFG_ID = '{query}_{url}_{starttime}'
    instance = None
    runtimeconfig = {CONFIG_CHANNEL: SPIDER_CHANNEL_S1, CONFIG_TYPE: '',
                          CONFIG_QUERY: ''}
    
     
    if constant.DEBUG_FLAG ==  constant.DEBUG_FLAG_WINDOWS:
        cmd = 'ipconfig'     
    else:
        cmd = 'ifconfig'   
    _starttime = None
    _localmachineflag = None
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        
    ################################################################################################################
    # @functions：getinstance
    # @param： none
    # @return：实例对象
    # @note：获取单实例对象
    ################################################################################################################
    @staticmethod
    def getinstance():
        if SpiderConfigure.instance is None:
            SpiderConfigure.instance = SpiderConfigure()
            SpiderConfigure.instance.readconfig()
        return SpiderConfigure.instance

    ################################################################################################################
    # @functions：readconfig
    # @param： none
    # @return：none
    # @note：读取配置文件
    ################################################################################################################
    def readconfig(self):
        conf = SpiderConfigure.CONFIG_FILE_PATH
        with open(conf, 'r') as cfgfile:
            self.config.readfp(cfgfile)

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    @staticmethod
    def getconfig(domain, key):
        return SpiderConfigure.getinstance().__getconfig(domain, key)

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def getchannel(self):
        return self.runtimeconfig.get(SpiderConfigure.CONFIG_CHANNEL)

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def gettype(self):
        return self.runtimeconfig.get(SpiderConfigure.CONFIG_TYPE)

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def getquery(self):
        return self.runtimeconfig.get(SpiderConfigure.CONFIG_QUERY)

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def setchannel(self, channel):
        self.runtimeconfig[SpiderConfigure.CONFIG_CHANNEL] = channel

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def settype(self, type):
        self.runtimeconfig[SpiderConfigure.CONFIG_TYPE] = type

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def setquery(self, query):
        self.runtimeconfig[SpiderConfigure.CONFIG_QUERY] = query

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def getlastdays(self):
        return int(self.__getconfig(const.SPIDER_S2_DOMAIN, const.SPIDER_QUERY_LAST_DAYS))

    ################################################################################################################
    # @functions：gets1file
    # @param： none
    # @return：s1 file
    # @note：返回s1的输入文件
    ################################################################################################################
    def gets1file(self):
        return self.__getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_S1_INPUT_FILE)

    ################################################################################################################
    # @functions：gets2file
    # @param： none
    # @return：s2 file
    # @note：返回s2的输入文件
    ################################################################################################################
    def gets2file(self):
        return self.__getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_S2_INPUT_FILE)

    ################################################################################################################
    # @functions：__getconfig
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def __getconfig(self, domain, key):
        return self.config.get(domain, key)

    ################################################################################################################
    # @functions：getmaxrecycletimesl
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def getmaxrecycletimesl(self):
        return int(self.__getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_S2_INPUT_FILE))

    ################################################################################################################
    # @functions：getvalidperiod
    # @param： none
    # @return：none
    # @note：SpiderConfigure初始化内部变量
    ################################################################################################################
    def getvalidperiod(self):
        return int(self.__getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_VALID_PERIOD))

    def starttime(self):
        if SpiderConfigure._starttime is None:
            SpiderConfigure._starttime = int(time.time())
        return SpiderConfigure._starttime
    
    #----------------------------------------------------------------------
    @staticmethod
    def getipflag():
        pattern = '(10\.\d+\.\d+\.\d+)'
        ip = ''
        try:
            print 'Execute Command: {cmd}'.format(cmd=SpiderConfigure.cmd)
            subp = subprocess.Popen(SpiderConfigure.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subp.wait()
            lines = subp.stdout.readlines()
            string = ''.join(lines)
            if re.search(pattern, string):
                ip = re.findall(pattern, string)[0]
                print 'Get local machine ip: {ip}'.format(ip=ip)
                return ip.replace('.','')
            print 'WARNNING: Get wrong local machine ip, {ip}'.format(ip='127.0.0.1')
            return '127.0.0.1'.replace('.','')
        except:
            traceback.print_exc()
            print 'WARNNING: Get wrong local machine ip, {ip}'.format(ip='127.0.0.1')
            return '127.0.0.1'.replace('.','')
 
    def localmachineflag(self):
        if not SpiderConfigure._localmachineflag:
            SpiderConfigure._localmachineflag = SpiderConfigure.getipflag()
        return SpiderConfigure._localmachineflag
    
    #----------------------------------------------------------------------
    @staticmethod
    def ismaster():
        value = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN, const.SPIDER_TENCENT_PLATFORM_SLAVE)
        if str(value).lower() == 'false':
            return False
        else:
            return True
            
    #----------------------------------------------------------------------
    @staticmethod
    def iswaibu():
        value = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN, const.SPIDER_TENCENT_PLATFORM_WAIBU)
        if str(value).lower() == 'false':
            return False
        else:
            return True 
    #----------------------------------------------------------------------
    @staticmethod
    def getwaibubaup():
        return SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_WAIBU_BACKUP_PATH) + TimeUtility.getcurrentdate()
        