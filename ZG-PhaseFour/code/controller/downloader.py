  # -*- coding: utf-8 -*-
###################################################################################################
# @file: diffcontroller.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note:
###################################################################################################
import os
import re
import time

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from storage.storage import Storage
from storage.urlfilemanager import URLFileManager
from tencentplatform.localdownloader import LocalDownloaderInfo
from tencentplatform.tencentdownloader import TaskInfo
from utility import const
from utility.fileutil import FileUtility
from utility.regexutil import RegexUtility
from utility.timeutility import TimeUtility
from tencentplatform.waibudownloader import WaibiDownloader, WaibiDownloaderInfo 
if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
    from test.tencentdowloadermock import TencentDownloader
    from test.localdowloadermock import LocalDownloader
elif constant.DEBUG_FLAG == constant.DEBUG_FLAG_LINUX:
    from test.tencentdowloader2 import TencentDownloader
    from tencentplatform.localdownloader import LocalDownloader
else:
    from tencentplatform.tencentdownloader import TencentDownloader
    from tencentplatform.localdownloader import LocalDownloader



################################################################################################################
# @class：Downloader
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Downloader:
    DOWNLOAD_FORMAT1 = '.*{file}\.txt\.\d+\..*'
    DOWNLOAD_FORMAT2 = '.*{file}\_split_(\d+)_(\d+)_\d+\.txt\.\d+\..*'
    FAIL_TASKLIST = 'fail_download_tasklist'
    FAIL_TOTAL = 'fail_download_total'

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.upload_file_list = {}
        self.impls = []
        self.implsindex = 0
        self.initcommon()
        self.wimpls = []
        self.wimplsindoex = 0
        self.initwebkit()
        self.limpls = []
        self.limplsindex = 0
        self.initlocal()
        self.tempurlpath = Storage.getstoragelocation(const.SPIDER_URLS_TEMP_PATH)
        self.urlbackuppath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                       const.SPIDER_URL_BACKUP_PATH) + TimeUtility.getcurrentdate()
        #文件下载失败重试机制
        self.retransmissionfiles = {}
        self.all_retransmissionfiles = {}
        self.retransmissionlimitnum = 3
        self.filetime = 0

    def initcommon(self):
        for task in SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                              const.SPIDER_TENCENT_PLATFORM_TASK_LIST).split(','):
            taskinfo = TaskInfo()
            task = task.strip()
            taskinfo.taskid = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                        task + constant.SPIDER_TASKID)
            taskinfo.taskname = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                          task + constant.SPIDER_TASKNAME)
            taskinfo.userid = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                        task + constant.SPIDER_USERID)
            self.impls.append(TencentDownloader(taskinfo))

    def initwebkit(self):
        for task in SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                              const.SPIDER_TENCENT_PLATFORM_WEBKIT_TASK_LIST).split(','):
            taskinfo = TaskInfo()
            task = task.strip()
            taskinfo.taskid = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                        task + constant.SPIDER_TASKID)
            taskinfo.taskname = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                          task + constant.SPIDER_TASKNAME)
            taskinfo.userid = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                        task + constant.SPIDER_USERID)
            self.wimpls.append(TencentDownloader(taskinfo))
            
    
    def initlocal(self):
        """"""
        for dl in SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                            const.SPIDER_LOCAL_DOWNLOADER_LIST).split(','):
            info = LocalDownloaderInfo()
            dl = dl.strip()
            info.ip = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                dl + constant.DOWNLOADER_IP)
            info.port = int(SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      dl + constant.DOWNLOADER_PORT))
            info.username = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      dl + constant.DOWNLOADER_USERNAME)
            info.password = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      dl + constant.DOWNLOADER_PASSWORD)
            info.urlpath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                     dl + constant.DOWNLOADER_URL_PATH)
            info.donepath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      dl + constant.DOWNLOADER_DONE_PATH)
            info.localdonepath = Storage.getstoragelocation(const.SPIDER_DONE_TEMP_PATH)
            info.jsonpath = Storage.getstoragelocation(const.SPIDER_JSON_TEMP_PATH)
            self.limpls.append(LocalDownloader(info))
    ################################################################################################################
    # @functions：upload
    # @param： 文件路径
    # @param： 异步还是同步
    # @return：上传后生成的文件
    # @note：上传文件到下载平台
    ################################################################################################################
    def __upload__(self, filepath):
        flag = True
        FileUtility.mkdirs(self.urlbackuppath)
        FileUtility.copy(filepath, self.urlbackuppath)
        self.upload_file_list[FileUtility.getfilename(filepath)] = []
        # if filepath.endswith(constant.POST_FILE_SUFFIX) or FileUtility.getfilelines(filepath) <= constant.REMOTE_DOWNLOADER_MIN_LINES:
        #     if self.limpls:
        #         if self.limplsindex >= len(self.limpls):
        #             self.limplsindex = 0
        #         flag = self.limpls[self.limplsindex].upload(filepath)
        #         self.limplsindex += 1
        if filepath.endswith(constant.WEBKIT_FILE_SUFFIX):
            if self.wimpls:
                if self.wimplsindoex >= len(self.wimpls):
                    self.wimplsindoex = 0
                self.wimpls[self.wimplsindoex].upload(filepath)
                self.wimplsindoex += 1                
        elif self.impls:
            if self.implsindex >= len(self.impls):
                self.implsindex = 0
            flag = self.impls[self.implsindex].upload(filepath)
            self.implsindex += 1
        else:
            flag = False
            Logger.getlogging().warning('No taskid or download platform!')
        return flag

    ################################################################################################################
    # @functions：uploadfiles
    # @param： 文件路径列表
    # @return：成功失败
    # @note：上传文件到下载平台
    ################################################################################################################
    def upload(self, upfiles):
        Logger.getlogging().debug('uploading ......')
        for file in upfiles:
            if self.emptyfile(file):
                Logger.getlogging().info('remove empty file: ' + file)
                FileUtility.remove(file)
                continue
            if not self.__upload__(file):
                Logger.log(FileUtility.getfilename(file), constant.ERRORCODE_FAIL_LOAD_UP)
                return False
            Logger.getlogging().info('remove uploadedfile' + file)
            FileUtility.remove(file)
        time.sleep(1)
        return True

    ################################################################################################################
    # @functions：emptyfile
    # @filepath： 文件路径列表
    # @return：是否为空文件
    # @note：判断文件是否为空文件
    ################################################################################################################
    def emptyfile(self, filepath):
        with open(filepath, 'r') as fp:
            for line in fp.readlines():
                if line.strip():
                    return False
        return True

    def retrans(self):
        if len(self.retransmissionfiles) > 0:
            # 从backup中恢复数据到temp/urls
            for fl in self.retransmissionfiles.keys():
                newfl = self.recoverfile(fl)
                newfilename = FileUtility.getfilename(newfl)
                self.all_retransmissionfiles[newfilename] = self.all_retransmissionfiles[fl]
                Logger.getlogging().debug('download fail and transimission file {fl}:{num}th'.format(fl=newfilename,
                                                                                                     num=self.all_retransmissionfiles[newfilename].retrans_num))
                                                                                                         
                impl = self.all_retransmissionfiles[newfilename].taskinfo
                if not impl.taskstatusflag:
                    if impl in self.wimpls:
                        if len(self.wimpls) != 1:
                            self.wimpls.remove(impl)
                            Logger.getlogging().warning(
                                'download fail and delete taskid is :{impl}'.format(impl=impl.taskinfo.taskid))
                        else:
                            Logger.getlogging().warning('only one taskid is :{impl}'.format(impl=impl.taskinfo.taskid))
                    if impl in self.impls:
                        if len(self.impls) != 1:
                            self.impls.remove(impl)
                            Logger.getlogging().warning(
                                'download fail and delete taskid is :{impl}'.format(impl=impl.taskinfo.taskid))
                        else:
                            Logger.getlogging().warning('only one taskid is :{impl}'.format(impl=impl.taskinfo.taskid))
                    if impl in self.limpls:
                        if len(self.limpls) != 1:
                            self.limpls.remove(impl)
                            Logger.getlogging().warning(
                                'download fail and delete downloadplatform is :{impl}'.format(impl=impl.info.ip))
                        else:
                            Logger.getlogging().warning(
                                'only one downloadplatform is :{impl}'.format(impl=impl.info.ip))
                self.retransmissionfiles.pop(fl)

    def recoverfile(self, filename):
        """"""
        # 查找，获取backup路径,再恢复到目的目录./data/temp/urls
        filelist = FileUtility.getfilelist(self.urlbackuppath, [])
        tempfilepath = os.path.join(self.urlbackuppath, filename)
        if tempfilepath in filelist:
            newfilepath = self.renewfilename(tempfilepath)
            FileUtility.copy(tempfilepath, newfilepath)
            time.sleep(0.5)
            if FileUtility.exists(newfilepath):
                return newfilepath
        return False

    # ----------------------------------------------------------------------
    def renewfilename(self, file):
        """"""
        filename = FileUtility.getfilename(file)
        context = URLFileManager.getinstance().geturlfilecontext(filename)
        if not context:
            return False
        if self.filetime == int(time.time()):
            time.sleep(1)
        self.filetime = int(time.time())
        newfilename = filename.replace(re.findall('\d+', filename)[-1], str(self.filetime))
        urlsfile = self.tempurlpath + newfilename
        context.filename = urlsfile
        URLFileManager.getinstance().updateurlfilecontext(FileUtility.getfilename(urlsfile), context)
        return urlsfile

    ################################################################################################################
    # @functions：download
    # @param： 上传时的文件名
    # @return：上传后生成的文件
    # @note：从下载平台下载文件
    ################################################################################################################
    def download(self):
        Logger.getlogging().debug('downloading ......')
        valid_json_files = []
        valid_json_files.extend(self.__download__(self.impls))
        valid_json_files.extend(self.__download__(self.wimpls))
        valid_json_files.extend(self.__download__(self.limpls))
        self.retrans()
        return valid_json_files

    ################################################################################################################
    # @functions：__download__
    # @param：downloaderlist 上传时的文件名
    # @param：valid_json_files 上传时的文件名
    # @return：上传后生成的文件
    # @note：从下载平台下载文件
    ################################################################################################################
    def __download__(self, downloaderlist):
        valid_json_files = []
        for impl in downloaderlist:
            json_files = impl.download()
            for dfile in json_files:
                for ufile in self.upload_file_list.keys():
                    if RegexUtility.match(Downloader.DOWNLOAD_FORMAT1.format(file=ufile), dfile):
                        self.upload_file_list.pop(ufile)
                        if FileUtility.exists(dfile):
                            valid_json_files.append(dfile)
                            Logger.getlogging().info('downloadedjsonfile\t' + dfile)
                    elif RegexUtility.match(Downloader.DOWNLOAD_FORMAT2.format(file=ufile), dfile):
                        value = RegexUtility.parse(Downloader.DOWNLOAD_FORMAT2.format(file=ufile), dfile)[0]
                        if FileUtility.exists(dfile):
                            valid_json_files.append(dfile)
                            Logger.getlogging().info('downloadedjsonfile\t' + dfile)
                        if value[0] == value[1]:
                            self.upload_file_list.pop(ufile)
            retransmissionfiles = impl.outtimefiles()
            for fl in retransmissionfiles.keys():
                # 下载异常
                if fl not in self.all_retransmissionfiles:
                    self.all_retransmissionfiles[fl] = retransmissionfiles[fl]
                self.all_retransmissionfiles[fl].retrans_num += 1
                self.all_retransmissionfiles[fl].taskinfo = impl
                self.retransmissionfiles[fl] = self.all_retransmissionfiles[fl]
                if self.retransmissionfiles[fl].retrans_num <= self.retransmissionlimitnum:
                    # 虽然下载失败了，但假装已下载，故在upload_file_list删除
                    self.upload_file_list.pop(fl)
                    Logger.getlogging().debug('download fail file {fl}:{num}th fail'.format(fl=fl, num=
                                                                                            self.all_retransmissionfiles[fl].retrans_num))
                else:
                    # 虽然下载失败了，但假装已下载，故在upload_file_list删除;不再重传，在重传列表中删除
                    self.upload_file_list.pop(fl)
                    self.retransmissionfiles.pop(fl)
                    Logger.getlogging().debug('download fail file {fl}:more then {num}th fail'.format(fl=fl, num=
                                                                                                      self.all_retransmissionfiles[fl].retrans_num - 1))
        return valid_json_files

    ################################################################################################################
    # @functions：iscompleted
    # @param： none
    # @return：True if all files is downloaded else False
    # @note：
    ################################################################################################################
    def iscompleted(self):
        if len(self.upload_file_list.keys()) == 0:
            return True
        else:
            return False

    ################################################################################################################
    # @functions：showremainfiles
    # @param： None
    # @return：None
    # @note：show not downloaded files
    ################################################################################################################
    def showremainfiles(self):
        Logger.getlogging().warning('Following files is not downloaded!')
        for file in self.upload_file_list.keys():
            Logger.getlogging().warning(file)



#######################################################################
#class SchedulDownloader(Downloader):
    #""""""

    ## ----------------------------------------------------------------------
    #def __init__(self):
        #"""Constructor"""
        #Downloader.__init__(self)

    ## ----------------------------------------------------------------------
    #def initpost(self):
        #""""""
        #for dl in SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                            #const.SPIDER_LOCAL_DOWNLOADER_LIST).split(','):
            #info = LocalDownloaderInfo()
            #dl = dl.strip()
            #info.ip = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                #dl + constant.DOWNLOADER_IP)
            #info.port = int(SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      #dl + constant.DOWNLOADER_PORT))
            #info.username = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      #dl + constant.DOWNLOADER_USERNAME)
            #info.password = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      #dl + constant.DOWNLOADER_PASSWORD)
            #info.urlpath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                     #dl + constant.DOWNLOADER_URL_PATH)
            #info.donepath = SpiderConfigure.getconfig(const.SPIDER_LOCAL_DOMAIN,
                                                      #dl + constant.DOWNLOADER_DONE_PATH)
            #info.localdonepath = SpiderConfigure.getconfig(const.SPIDER_SCHEDULER_DOMAIN,
                                                           #const.SCHEDULER_DONE_PATH)
            #self.pimpls.append(LocalDownloader(info))

########################################################################
class WDownloader:
    
    #----------------------------------------------------------------------
    def __init__(self):
        self.wbimpls = {}
        self.tasknamelist = {}
        self.initwaibu()        
        
        
    #----------------------------------------------------------------------
    def initwaibu(self):
        for dl in SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                            const.SPIDER_TENCENT_PLATFORM_WBTASK_LIST).split(','):
            info = WaibiDownloaderInfo()
            info.taskname = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                  dl + constant.SPIDER_WBTASK_NAME)
            info.token = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                   dl + constant.SPIDER_WBTASK_TOKEN)
            info.appid = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN,
                                                   dl + constant.SPIDER_WBTASK_APPID)
            self.wbimpls[WaibiDownloader(info)] = ''
            self.tasknamelist[info.taskname] = ''
        
    #----------------------------------------------------------------------
    def upload(self, upfile):
        for wbimpl in self.wbimpls:
            wbimpl.upload(upfile)
            time.sleep(3)
    
    def download(self):
        downfiles = []
        for wbimp in self.wbimpls.keys():
            if wbimp.checkstatus():
                waibufiles = wbimp.download()
                for wfile in waibufiles:  
                    for taskname in self.tasknamelist.keys():
                        if taskname in wfile:   
                            self.tasknamelist.pop(taskname)
                            self.wbimpls.pop(wbimp)
                            downfiles.append(wfile)
        return downfiles
        
    def iscompleted(self):
        if not self.tasknamelist:
            return True
        return False
        
            
            
        
        
        
        
    
    