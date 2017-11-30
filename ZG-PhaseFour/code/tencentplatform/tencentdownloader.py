# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import subprocess

from log.spidernotify import SpiderNotify, NotifyParam
from utility.fileutil import FileUtility
from configuration import constant
from configuration.constant import const
from configuration.environment.configure import SpiderConfigure
from configuration.constant import const
from utility.common import Common
from utility.regexutil import RegexUtility
from storage.storage import Storage
from log.spiderlog import Logger
import time
import os


################################################################################################################
# @class：TencentDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：Tencent download platform
################################################################################################################
class TencentDownloader:
    # upload command
    UPLOAD_COMMAND = 'curl -F "url_upload=@{file}" "{url}?user_id={user_id}&task_name={task_name}&task_id={task_id}"'
    # download path
    DOWNLOAD_PATH = '{path}/{taskid}/cout'
    # pars command
    PARSE_COMMAND = '{command} {input} {output}/{filename}'

    DOWNLOAD_FORMAT1 = '.*{file}\.txt\.\d+\..*'
    DOWNLOAD_FORMAT2 = '.*{file}\_split_(\d+)_(\d+)_\d+\.txt\.\d+\..*'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self, taskinfo):
        self.taskinfo = taskinfo
        self.upload_url = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                    const.SPIDER_TENCENT_PLATFORM_UPLOAD_URL)
        self.cache_path = Storage.getstoragelocation(const.SPIDER_DONE_TEMP_PATH)
        path = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                         const.SPIDER_TENCENT_PLATFORM_OUTPUT_PATH)
        self.download_path = TencentDownloader.DOWNLOAD_PATH.format(
            path=path, taskid=self.taskinfo.taskid)

        self.parse_tool = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                    const.SPIDER_TENCENT_PLATFORM_PARSE_TOOL)
        self.parse_tool_img = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                        const.SPIDER_TENCENT_PLATFORM_PARSE_TOOL_IMG)
        self.json_path = Storage.getstoragelocation(const.SPIDER_JSON_TEMP_PATH)
        self.upload_file_list = {}
        self.recycle_times = 0
        self.download_file_list = []
        self.download_file_list2 = []
        self.retrytimes = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN,
                                                        const.SPIDER_UPLOAD_RETRY_TIMES))
        # 新添加的变量
        self.uploadfile_retranslist = {}
        self.outtimelimit = int(
            SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_WAIT_PLATFORM_TIMEOUT))
        # self.outtimelimit = 10
        self.download_time = time.time()
        self.taskstatusflag = True
        self.start_time = 0

    ################################################################################################################
    # @functions：upload
    # @param： upload file path
    # @return：True if upload successfully, False if too many files have uploaded
    # @note：upload file to Tencent download platform
    ################################################################################################################
    def upload(self, path):
        retans = RetransInfo()
        retans.filename = FileUtility.getfilename(path)
        if int(self.start_time) == int(time.time()):
            time.sleep(0.1)
        self.start_time = time.time()
        retans.start_time = self.start_time
        self.uploadfile_retranslist[retans.filename] = retans
        self.upload_file_list[FileUtility.getfilename(path)] = []
        cmd = TencentDownloader.UPLOAD_COMMAND.format(file=path, url=self.upload_url, user_id=self.taskinfo.userid,
                                                      task_name=self.taskinfo.taskname, task_id=self.taskinfo.taskid)
        if self.execute(cmd):
            return True
        secs = 10
        for count in range(0, self.retrytimes):
            time.sleep(secs)
            secs *= 2
            if self.execute(cmd):
                return True
        else:
            param = NotifyParam()
            param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
            param.message = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT.format(
                file=FileUtility.getfilename(path), taskid=self.taskinfo.taskid)
            SpiderNotify.notify(param)
            return False

    ################################################################################################################
    def download(self):
        """
        平台上的下载分为两个步骤,而windows直接请求数据则只有step2:download()
        step1:从平台上下载数据到本地./data/platform
        step2:从./data/platform拷贝数据到./data/temp/done下,再存储解析后的json数据至./data/temp/json
        """
        files = []
        if self.completed():
            return files
        Logger.getlogging().debug(self.download_path)
        srclist = FileUtility.getfilelist(self.download_path, [])
        for donefile in srclist:
            filename = FileUtility.getfilename(donefile)
            if donefile.endswith('done') and filename not in self.download_file_list:
                self.download_file_list.append(filename)
                self.download_time = time.time()
                for upfile in self.upload_file_list.keys():
                    if filename.startswith(upfile):
                        FileUtility.copy(donefile, self.cache_path)
                        binfile = self.cache_path + FileUtility.getfilename(donefile)
                        if FileUtility.getfilesize(donefile) == FileUtility.getfilesize(binfile):
                            Logger.getlogging().info('Remove {file}'.format(file=donefile))
                            FileUtility.remove(donefile)
                            if FileUtility.exists(donefile):
                                Logger.getlogging().error('Remove {file} failed'.format(file=donefile))
                        else:
                            Logger.getlogging().error('File not equal {file}'.format(file=donefile))
                        jsonfile = self.bin2json(binfile)
                        files.append(jsonfile)
                        uploadtime = self.uploadfile_retranslist[upfile].start_time
                        if RegexUtility.match(TencentDownloader.DOWNLOAD_FORMAT1.format(file=upfile), filename):
                            self.upload_file_list.pop(upfile)
                            self.uploadfile_retranslist.pop(upfile)
                        elif RegexUtility.match(TencentDownloader.DOWNLOAD_FORMAT2.format(file=upfile), filename):
                            value = \
                            RegexUtility.parse(TencentDownloader.DOWNLOAD_FORMAT2.format(file=upfile), filename)[0]
                            if value[0] == value[1]:
                                self.upload_file_list.pop(upfile)
                                self.uploadfile_retranslist.pop(upfile)
                        if not FileUtility.exists(jsonfile):
                            Logger.getlogging().error(
                                'no json file generate from done file:{done}'.format(done=binfile))
                            os.mknod(jsonfile)
                        # update upload time
                        keys = self.sortkeys()
                        for fl in keys:
                            if self.uploadfile_retranslist[fl].start_time >= uploadtime:
                                self.uploadfile_retranslist[fl].start_time = time.time()
                                time.sleep(0.1)
                        break
        return files

    def sortkeys(self):
        filelist = sorted(self.uploadfile_retranslist.iteritems(), key=lambda d: d[1].start_time)
        keys = [item[0] for item in filelist]
        return keys

    ################################################################################################################
    # @functions：bin2json
    # @param： done file
    ##### @return：json file/
    # @note：convert done file to json file using parse tool
    ################################################################################################################
    def bin2json(self, file):
        filename = FileUtility.getfilename(file).replace('.done', '.json')
        tool = self.parse_tool
        if constant.IMG_FILE_SUFFIX in filename:
            tool = self.parse_tool_img
        cmd = TencentDownloader.PARSE_COMMAND.format(
            command=tool,
            input=file,
            output=self.json_path,
            filename=filename)
        self.execute(cmd)
        return self.json_path + filename

    ################################################################################################################
    # @functions：execute
    # @param： command
    # @return：none
    # @note：execute command
    ################################################################################################################
    def execute(self, cmd):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd=cmd))
        subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subp.wait()
        c = subp.stdout.readline()
        while c:
            if subp.returncode != 0:
                Logger.getlogging().error(c.strip())
            else:
                Logger.getlogging().info(c.strip())
            c = subp.stdout.readline()
        e = subp.stderr.readline()
        while e:
            if subp.returncode != 0:
                Logger.getlogging().error(e.strip())
            else:
                Logger.getlogging().info(e.strip())
            e = subp.stderr.readline()
        if subp.returncode != 0:
            Logger.getlogging().error('Execute command:{cmd} failed'.format(cmd=cmd))
            return False
        return True

    ################################################################################################################
    # @functions：iscompleted
    # @param： none
    # @return：True if all files downloaded else False
    # @note：
    ################################################################################################################
    def completed(self):
        return not self.upload_file_list

    # ----------------------------------------------------------------------
    def outtimefiles(self):
        retransmissionfiles = {}
        if not self.uploadfile_retranslist:
            return retransmissionfiles
        current_time = time.time()
        for fl in self.uploadfile_retranslist.keys():
            start_time = self.uploadfile_retranslist[fl].start_time
            if current_time - start_time > self.outtimelimit:
                retransmissionfiles[fl] = self.uploadfile_retranslist[fl]
                self.upload_file_list.pop(fl)
                self.uploadfile_retranslist.pop(fl)
        if retransmissionfiles:
            if current_time - self.download_time > self.outtimelimit:
                self.taskstatusflag = False
                for fl in self.uploadfile_retranslist.keys():
                    retransmissionfiles[fl] = self.uploadfile_retranslist[fl]
                    self.upload_file_list.pop(fl)
                    self.uploadfile_retranslist.pop(fl)
        return retransmissionfiles


class TaskInfo:
    def __init__(self):
        self.taskid = ''
        self.taskname = ''
        self.userid = ''


########################################################################
class RetransInfo:
    def __init__(self):
        """Constructor"""
        self.filename = ''
        self.start_time = 0
        self.end_time = 0
        self.taskinfo = None
        self.retrans_num = 0
        self.taskstatusflag = True


if __name__ == '__main__':
    os.chdir('..')
    ti = TaskInfo()
    ti.taskid = ''
    TencentDownloader(ti).execute('curl http://www.baidu.com')
