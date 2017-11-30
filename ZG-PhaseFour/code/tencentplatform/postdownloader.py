# encoding=utf-8
##############################################################################################
# @file：postdownloader.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：
##############################################################r################################
from log.spidernotify import SpiderNotify, NotifyParam
from utility import ssh
from utility.fileutil import FileUtility
from log.spiderlog import Logger
import time
from configuration import constant
from configuration.constant import const
from configuration.environment.configure import SpiderConfigure
################################################################################################################
# @class：PostDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：download platform
################################################################################################################
class PostDownloader:
    # upload command
    UPLOAD_COMMAND = 'scp {file} {username}@{ip}:{urlpath}'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self, info):
        self.info = info
        self.upload_file_list = {}
        self.recycle_times = 0
        self.download_file_list = []
        #新添加的变量
        self.uploadfile_retranslist = {}
        self.outtimelimit = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_WAIT_PLATFORM_TIMEOUT))
        #self.outtimelimit = 30
        self.download_time = 0  
        self.taskstatusflag = True
    ################################################################################################################
    # @functions：upload
    # @param： upload file path
    # @return：True if upload successfully, False if too many files have uploaded
    # @note：upload file to download platform
    ################################################################################################################
    def upload(self, path):
        retans = RetransInfo()
        retans.filename = FileUtility.getfilename(path)
        retans.start_time = int(time.time())
        self.uploadfile_retranslist[retans.filename] = retans
        self.upload_file_list[FileUtility.getfilename(path)] = []
        if self.sshupload(path):
            return True
        else:
            param = NotifyParam()
            param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
            param.message = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT.format(
                file=FileUtility.getfilename(path), taskid=self.info.ip)
            SpiderNotify.notify(param)
            return False

    ################################################################################################################
    # @functions：download
    # @param： none
    # @return： downloaded files
    # @note：get the files from download platform
    ################################################################################################################
    def download(self):
        files = []
        if self.completed():
            return files
        Logger.getlogging().debug(self.info.donepath)
        srclist = self.sshls(self.info.donepath)
        for donefile in srclist:
            donefile = donefile.strip()
            filename = FileUtility.getfilename(donefile)
            if donefile.endswith('done') and filename not in self.download_file_list:
                self.download_file_list.append(filename)
                for upfile in self.upload_file_list.keys():
                    if filename.startswith(upfile):
                        FileUtility.mkdirs(self.info.localdonepath)
                        self.sshdownload(donefile)
                        dfile = self.info.localdonepath + FileUtility.getfilename(donefile)
                        if self.info.jsonpath:
                            dfile = self.bin2json(dfile)
                        files.append(dfile)
                        self.download_time = int(time.time())
                        self.upload_file_list.pop(upfile)
                        self.uploadfile_retranslist.pop(upfile)
                        if not FileUtility.exists(dfile):
                            Logger.getlogging().error(
                                'no json file generate from done file:{done}'.format(done=dfile))
                        break
        return files


    def sshupload(self, path):
        return ssh.sshupload(self.info.ip, self.info.port, self.info.username, self.info.password, self.info.urlpath, path)

    def sshls(self, path):
        return ssh.sshls(self.info.ip, self.info.port, self.info.username, self.info.password, path)

    def sshdownload(self, donefile):
        ssh.sshdownload(self.info.ip, self.info.port, self.info.username, self.info.password,
                        self.info.donepath + donefile, self.info.localdonepath)

    ################################################################################################################
    # @functions：bin2json
    # @param： done file
    # @return：json file
    # @note：convert done file to json file using parse tool
    ################################################################################################################
    def bin2json(self, file):
        filename = FileUtility.getfilename(file).replace('.done', '.json')
        fullpath = self.info.jsonpath + filename
        FileUtility.copy(file, fullpath)
        return fullpath

    ################################################################################################################
    # @functions：initialize
    # @param： none
    # @return：none
    # @note：
    ################################################################################################################
    def initialize(self):
        files = ssh.sshls(self.info.ip, self.info.port, self.info.username, self.info.password, self.info.donepath)
        for fl in files:
            fl = fl.strip()
            self.download_file_list.append(FileUtility.getfilename(fl))

    ################################################################################################################
    # @functions：iscompleted
    # @param： none
    # @return：True if all files downloaded else False
    # @note：
    ################################################################################################################
    def completed(self):
        return not self.upload_file_list
    
    #----------------------------------------------------------------------
    def outtimefiles(self):
        retransmissionfiles = {}
        if not self.uploadfile_retranslist:
            return retransmissionfiles
        current_time = int(time.time())
        for fl in self.uploadfile_retranslist.keys():
            start_time = self.uploadfile_retranslist[fl].start_time
            if current_time - start_time > self.outtimelimit:
                retransmissionfiles[fl] = self.uploadfile_retranslist[fl]
                self.upload_file_list.pop(fl)
                self.uploadfile_retranslist.pop(fl)
        if retransmissionfiles:
            if not self.download_time or (current_time - self.download_time > self.outtimelimit):
                self.taskstatusflag = False
                for fl in self.uploadfile_retranslist.keys():
                    retransmissionfiles[fl] = self.uploadfile_retranslist[fl]
                    self.upload_file_list.pop(fl)
                    self.uploadfile_retranslist.pop(fl)
        return retransmissionfiles

class PostDownloaderInfo:
    def __init__(self):
        self.ip = 'localhost'
        self.port = 22
        self.username = 'root'
        self.password = ''
        self.urlpath = ''
        self.donepath = ''
        self.jsonpath = ''
        self.localdonepath = ''
        
class RetransInfo:
    def __init__(self):
        """Constructor"""
        self.filename = ''
        self.start_time = 0
        self.end_time = 0
        self.taskinfo = None
        self.retrans_num = 0
        