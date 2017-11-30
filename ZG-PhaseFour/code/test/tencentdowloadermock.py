# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import time
from utility.fileutil import FileUtility
from log.spiderlog import Logger
import tencentplatform.tencentdownloader


class TencentDownloader(tencentplatform.tencentdownloader.TencentDownloader):

    def __init__(self, taskinfo):
        tencentplatform.tencentdownloader.TencentDownloader.__init__(self, taskinfo)
        self.download_path = TencentDownloader.DOWNLOAD_PATH.format(
            path='./data/platform', taskid=taskinfo.taskid)

    def bin2json(self, file):
        jsonfile = tencentplatform.tencentdownloader.TencentDownloader.bin2json(self, file)
        FileUtility.copy(file, jsonfile)
        return jsonfile

    def execute(self, cmd):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd = cmd))
        return True

    def upload(self, path):
        tencentplatform.tencentdownloader.TencentDownloader.upload(self, path)
        filename = FileUtility.getfilename(path)
        ts = int(time.time())
        FileUtility.mkdirs(self.download_path)
        Logger.getlogging().debug(path+'--->'+'{dir}/{filename}.txt.{ts}.done'.format(dir=self.download_path, filename=filename, ts=int(time.time())))   
        FileUtility.copy(path, '{dir}/{filename}.txt.{ts}.done'.format(dir=self.download_path, filename=filename, ts=int(time.time())))
        return True
