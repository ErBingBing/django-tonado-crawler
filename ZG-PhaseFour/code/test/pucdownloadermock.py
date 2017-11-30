# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import subprocess

import tencentplatform.pucdownloader
from utility.fileutil import FileUtility
from log.spiderlog import Logger


################################################################################################################
# @class：TencentDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：Tencent download platform
################################################################################################################
class PUCDownloader(tencentplatform.pucdownloader.PUCDownloader):

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self, taskinfo):
        tencentplatform.pucdownloader.PUCDownloader.__init__(self, taskinfo)
        self.download_path = PUCDownloader.DOWNLOAD_PATH.format(
            path='./data/platform', taskid=taskinfo.taskid)

    ################################################################################################################
    # @functions：bin2json
    # @param： done file
    ##### @return：json file/
    # @note：convert done file to json file using parse tool
    ################################################################################################################
    def bin2json(self, file):
        jsonfile = tencentplatform.pucdownloader.PUCDownloader.bin2json(self, file)
        FileUtility.copy(file, jsonfile)
        return jsonfile

    ################################################################################################################
    # @functions：execute
    # @param： command
    # @return：none
    # @note：execute command
    ################################################################################################################
    def execute(self, cmd):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd = cmd))
        return True
