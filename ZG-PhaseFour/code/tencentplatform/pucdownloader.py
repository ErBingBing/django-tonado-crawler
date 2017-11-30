# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import subprocess

from utility.fileutil import FileUtility
from configuration.environment.configure import SpiderConfigure
from configuration.constant import const
from storage.storage import Storage
from log.spiderlog import Logger
from utility.timeutility import TimeUtility
import os
import re
import time
import json
from storage.newsstorage import NewsStorage
from utility.common import Common
from configuration import constant
################################################################################################################
# @class：TencentDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：Tencent download platform
################################################################################################################
class PUCDownloader:
    # download path
    DOWNLOAD_PATH = '{path}/{taskid}/mout'
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
    def __init__(self, taskinfo=None, download_path=None):
        self.taskinfo = taskinfo
        self.maxfilenum = 100
        self.cache_path = Storage.getstoragelocation(const.SPIDER_DONE_TEMP_PATH)
        path = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                         const.SPIDER_TENCENT_PLATFORM_OUTPUT_PATH)
        if download_path:
            self.download_path = download_path
        else:
            self.download_path = PUCDownloader.DOWNLOAD_PATH.format(
                path=path, taskid=self.taskinfo.taskid)
        self.parse_tool = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                    const.SPIDER_TENCENT_PLATFORM_PARSE_TOOL_IMG)
        #self.json_path = Storage.getstoragelocation(const.SPIDER_JSON_TEMP_PATH)
        self.pucbackpath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_PUC_BACKUP_PATH) + self.taskinfo.taskid
        self.pucbacktoday = os.path.join(self.pucbackpath,TimeUtility.getcurrentdate())
        if not FileUtility.exists(self.pucbackpath):
            FileUtility.mkdirs(self.pucbackpath)        
        if not FileUtility.exists(self.pucbacktoday):
            FileUtility.mkdirs(self.pucbacktoday)
        self.done_file = self.pucbacktoday+'/done/'
        self.json_path = self.pucbacktoday+'/json/'
        if not FileUtility.exists(self.done_file):
            FileUtility.mkdirs(self.done_file)       
        if not FileUtility.exists(self.json_path):
            FileUtility.mkdirs(self.json_path)             
        self.pucsavedays = 0
        self.clear()
    ################################################################################################################
    def download(self):
        """
        平台上的下载分为两个步骤,而windows直接请求数据则只有step2:download()
        step1:从平台上下载数据到本地./data/platform
        step2:从./data/platform拷贝数据到./data/temp/done下,再存储解析后的json数据至./data/temp/json
        """
        files = []
        Logger.getlogging().debug('Get Valid PUC File From ' + self.download_path)
        #srclist = self.getvalidfiles(self.download_path)
        srclist = FileUtility.getfilelist(self.download_path, [])[0:self.maxfilenum]
        for donefile in srclist:
            try:
                if donefile.endswith('done'):
                    Logger.getlogging().info('MOVE {file} TO {path}'.format(file=donefile,path=self.done_file))
                    FileUtility.move(donefile, self.done_file)  
                    binfile = os.path.join(self.done_file, FileUtility.getfilename(donefile))
                    #FileUtility.copy(donefile, self.cache_path)
                    #binfile = self.cache_path+ FileUtility.getfilename(donefile)
                    #if FileUtility.getfilesize(donefile) == FileUtility.getfilesize(binfile):
                        ##备份当天的puc文件
                        #Logger.getlogging().info('MOVE {file} TO {path}'.format(file=donefile,path=self.pucbacktoday))
                        #FileUtility.move(donefile, self.pucbacktoday)
                        #if FileUtility.exists(donefile):
                            #Logger.getlogging().error('MOVE {file} failed'.format(file=donefile))
                    #else:
                        #Logger.getlogging().error('File not equal {file}'.format(file=donefile))
                    jsonfile = self.bin2json(binfile)
                    files.append(jsonfile)
                    try:
                        self.s3puc_dumpurls(jsonfile)
                        time.sleep(0.5)
                        Logger.getlogging().debug('Remove {f}'.format(f=jsonfile))
                        FileUtility.remove(jsonfile)
                        donefile2 = os.path.join(self.done_file, FileUtility.getfilename(donefile))
                        Logger.getlogging().debug('Remove {f}'.format(f=donefile2))
                        FileUtility.remove(donefile2)
                    except:
                        Logger.printexception()
                        Logger.getlogging().error(
                            'no json file generate from done file:{done}'.format(done=binfile))
                        os.mknod(jsonfile)
            except:
                Logger.printexception()
        return files
        
    ################################################################################################################
    # @functions：bin2json
    # @param： done file
    ##### @return：json file/
    # @note：convert done file to json file using parse tool
    ################################################################################################################
    def bin2json(self, file):
        filename = FileUtility.getfilename(file).replace('.done', '.json')
        cmd = PUCDownloader.PARSE_COMMAND.format(
            command=self.parse_tool,
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
    
    #  保留当前文件
    #1.先找出当前文件的时间最大值t1
    #2.只取大于t1的文件
    def findmax(self):
        filelist = FileUtility.getfilelist(self.pucbackpath,[])
        tf = {}
        for f in filelist:
            t = int(re.findall('(\d+)',f)[-1])
            tf[t]=f
        if not tf:
            return 0
        tm = max(tf.keys())
        for f in filelist:
            t = int(re.findall('(\d+)',f)[-1])
            if t < tm:
                Logger.getlogging().info('REMOVE {file}'.format(file=f))
                FileUtility.remove(f)
        return tm
        
    def getvalidfiles(self, path):
        temmax = self.findmax()
        validfiles = []
        filelist = FileUtility.getfilelist(path, [])
        
        for f in filelist:
            t = int(re.findall('(\d+)',f)[-1])
            if t >= temmax:                
                validfiles.append(f)
        # 每次只获取前100个PUC文件
        return validfiles[:self.maxfilenum]
        
    def clear(self):
        dirlist = os.listdir(self.pucbackpath)
        for tm in dirlist:
            if tm < TimeUtility.getdatebefore(self.pucsavedays,TimeUtility.DATE_FORMAT_DEFAULT):
                FileUtility.rmdir(os.path.join(self.pucbackpath, tm))
                     
    @staticmethod
    def s3puc_dumpurls(pucfile):
        ends = '\.(cn|com|org|net|me)/?$'
        with open(pucfile, 'r') as fp:
            for line in fp.readlines():
                try:
                    if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
                        url = line.strip()
                    else:
                        url = Common.urldec(json.loads(line.strip())['url'])
                        if re.search(ends, url):
                            continue
                    NewsStorage.storeurl(url)
                except:
                    Logger.printexception()    