# -*- coding: utf-8 -*-
##############################################################################################
# @file: spidernotify.py
# @author: Sun Xinghua
# @date:  2016/12/2 9:18
# @version: Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import re
import socket
import subprocess
import urllib2

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from utility import const


class SpiderNotify:

    MESSEAGE_FORMAT = 'IP:{ip} PATH:{path} MSG:{msg}'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化日志
    ################################################################################################################
    @staticmethod
    def notify(params):
        tools = SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_REPORT_EXCEPTION_TOOL)
        Logger.getlogging().critical('NOTIFY:{msg}'.format(msg=params.message))
        info = SpiderNotify.MESSEAGE_FORMAT.format(ip=SpiderNotify.getip(), path=os.getcwd(), msg=params.message)
        SpiderNotify.execute(tools.format(message=info))

    ################################################################################################################
    # @functions：execute
    # @param： command
    # @return：none
    # @note：execute command
    ################################################################################################################
    @staticmethod
    def execute2(cmd):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd=cmd))
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_OFF and os.system(cmd) != 0:
            Logger.getlogging().error('Execute command:{cmd} failed'.format(cmd=cmd))
            return False
        return True

    ################################################################################################################
    # @functions：execute
    # @param： command
    # @return：none
    # @note：execute command
    ################################################################################################################
    @staticmethod
    def execute(cmd):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd=cmd))
        if constant.DEBUG_FLAG != constant.DEBUG_FLAG_OFF:
            return True
        subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subp.wait()
        c = subp.stdout.readline()
        while c:
            if subp.returncode != 0:
                Logger.getlogging().error(c.strip())
            else:
                Logger.getlogging().info(c.strip())
            c = subp.stdout.readline()
        if subp.returncode != 0:
            Logger.getlogging().error('Execute command:{cmd} failed'.format(cmd=cmd))
            return False
        return True

    ################################################################################################################
    # @functions：getip
    # @param： none
    # @return：none
    # @note：get ip
    ################################################################################################################
    @staticmethod
    def getip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 0))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
            return IP


################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class NotifyParam:
    SPIDER_NOTIFY_TIMEOUT = 1
    SPIDER_NOTIFY_OVER_RECYCLE = 2
    SPIDER_NOTIFY_INPUT_ERROR = 3
    SPIDER_NOTIFY_EXCEPTION = 4
    SPIDER_NOTIFY_OVER_FAILED = 5
    SPIDER_NOTIFY_UPLOAD_FAILED = 6
    SPIDER_NOTIFY_UNKNOWN = 999

    SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT = 'upload file:{file} to taskid:{taskid} failed'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化日志
    ################################################################################################################
    def __init__(self):
        self.code = 0
        self.message = ''
        self.file = os.path.abspath(__file__)


import os

if __name__ == '__main__':

    os.chdir('..')
    param = NotifyParam()
    param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
    param.message = 'upload error'
    SpiderNotify.notify(param)
