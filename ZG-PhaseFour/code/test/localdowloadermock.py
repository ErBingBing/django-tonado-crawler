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
import tencentplatform.localdownloader


class LocalDownloader(tencentplatform.localdownloader.LocalDownloader):

    def __init__(self, taskinfo):
        tencentplatform.localdownloader.LocalDownloader.__init__(self, taskinfo)
        self.download_path = './data/post/'

    #def bin2json(self, file):
        #jsonfile = tencentplatform.localdownloader.LocalDownloader.bin2json(self, file)
        #FileUtility.copy(file, jsonfile)
        #return jsonfile

    #def execute(self, cmd):
        #Logger.getlogging().info('Execute command:{cmd}'.format(cmd = cmd))
        #return True

    #def upload(self, path):
        #tencentplatform.localdownloader.LocalDownloader.upload(self, path)
        #filename = FileUtility.getfilename(path)
        #FileUtility.mkdirs(self.download_path)
        #FileUtility.copy(path, '{dir}/{filename}.txt.{ts}.done'.format(dir=self.download_path, filename=filename, ts=int(time.time())))
        #return True

    #def sshupload(self, path):
        #Logger.getlogging().info('sshupload:' + path)
        #return True

    #def sshdownload(self, donefile):
        #Logger.getlogging().info('sshdownload:' + donefile)
        #FileUtility.copy(donefile, self.info.localdonepath)

    #def sshls(self, path):
        #return FileUtility.getfilelist(self.download_path, [])
