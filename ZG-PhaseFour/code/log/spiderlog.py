# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import traceback

from configuration.environment.configure import SpiderConfigure
from configuration.constant import const
from configuration import constant
import logging
import logging.config

################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility


class Logger:
    # 初始化标志
    __initialized = False
    __errorfile = None

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化日志
    ################################################################################################################
    def __init__(self):
        if not Logger.__initialized:
            file = SpiderConfigure.getinstance().getconfig(const.SPIDER_LOGGING_DOMAIN, const.SPIDER_LOG_CONFIGURE_FILE)
            logging.config.fileConfig(file)
            Logger.__initialized = True

    ################################################################################################################
    # @functions：getlogging
    # @param： none
    # @return：none
    # @note：获取log
    ################################################################################################################
    @staticmethod
    def getlogging():
        if not Logger.__initialized:
            Logger()
        return logging.getLogger("debuglogger")

    @staticmethod
    def log(url, ecode):
        if str(ecode).startswith('5000') or str(ecode).startswith('3000'):
            Logger.getlogging().warning(
                u'{url} errorcode:{code},message:{info}'.format(url=url,code=ecode,info=constant.ERRORINFO.get(
                    int(ecode),constant.ERRORINFO[constant.ERRORCODE_WARNNING_OTHERS])))
        else:
            Logger.getlogging().error(
                u'{url} errorcode:{code},message:{info}'.format(url=url,code=ecode,info=constant.ERRORINFO.get(
                    int(ecode),constant.ERRORINFO[constant.ERRORCODE_WARNNING_OTHERS])))        
        #if Logger.__errorfile is None:
            #Logger.__errorfile = SpiderConfigure.getinstance().getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                                         #const.SPIDER_URL_RESULT_ERROR_FILE).format(
                #date=TimeUtility.getcurrentdate())
            #FileUtility.remove(Logger.__errorfile)
        #FileUtility.writeline(Logger.__errorfile,
                              #'{channel},{query},{url},{code}'.format(
                                  #channel=SpiderConfigure.getinstance().getchannel(),
                                  #query=SpiderConfigure.getinstance().getquery(), url=url,
                                  #code=ecode))

    ################################################################################################################
    # @functions：exception
    # @param： none
    # @return：none
    # @note：获取log
    ################################################################################################################
    @staticmethod
    def printexception():
        s = traceback.format_exc()
        for line in s.split('\n'):
            Logger.getlogging().error(line)


# 全局变量初始化
# logger = Logger()

import os

if __name__ == '__main__':
    os.chdir('..')
    try:
        a = None
        b = 1
        a.eab()
    except:
        Logger.printexcept()
