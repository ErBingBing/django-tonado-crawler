# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
from tencentplatform import tencentdownloader
from utility.fileutil import FileUtility
from log.spiderlog import Logger


################################################################################################################
# @class：TencentDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：Tencent download platform
################################################################################################################
from utility.httputil import HttpUtility
from utility.xpathutil import XPathUtility


class TencentDownloader(tencentdownloader.TencentDownloader):

    DONE_FILE_URL = r'http://10.222.14.235/spider/{taskid}/cout/'
    DOWNLOAD_COMMAND = 'wget http://10.222.14.235/spider/{taskid}/cout/{filename}'
    HTTP_MAX_RETRY = 3

    def __init__(self, taskinfo):
        self.downloadedfiles = []
        tencentdownloader.TencentDownloader.__init__(self, taskinfo)
        self.download_path = TencentDownloader.DOWNLOAD_PATH.format(
            path='./data/platform', taskid=self.taskinfo.taskid)

    ################################################################################################################
    # @functions：download
    # @param： none
    # @return： downloaded files
    # @note：get the files from Tencent download platform
    ################################################################################################################
    def download(self):
        doneurl = TencentDownloader.DONE_FILE_URL.format(taskid=self.taskinfo.taskid)
        html = TencentDownloader.httpget(doneurl)
        if html:
            xparse = XPathUtility(html)
            for donefile in xparse.getlist(r'//tr/td[2]/a'):
                if donefile.endswith('done') and donefile not in self.downloadedfiles:
                    for upfile in self.upload_file_list:
                        if donefile.startswith(upfile):
                            FileUtility.mkdirs(self.download_path)
                            self.execute(TencentDownloader.DOWNLOAD_COMMAND.format(taskid=self.taskinfo.taskid, filename=donefile))
                            FileUtility.move('./' + donefile, self.download_path)
                            break
                    self.downloadedfiles.append(donefile)
        return tencentdownloader.TencentDownloader.download(self)

    def initialize(self):
        pass

    @staticmethod
    def httpget(url):
        for index in range(0, TencentDownloader.HTTP_MAX_RETRY):
            html = HttpUtility().get(url)
            if html:
                return html
        else:
            Logger.getlogging().error('Network is not unreachable!')
            exit(-1)
