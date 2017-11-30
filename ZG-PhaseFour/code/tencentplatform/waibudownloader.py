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
from storage.storage import Storage
from log.spiderlog import Logger
from utility.httputil import HttpUtility
import time
import os
import json
import urllib

################################################################################################################
# @class：TencentDownloader
# @author：Sun Xinghua
# @date：2016/12/06 9:44
# @note：Tencent download platform
################################################################################################################
class WaibiDownloader:
    # upload command
    #外部数据传入task信息  
    #UPLOADCMD = "curl -X POST  'http://api.rhino.datastory.com.cn/external/job/create?appId={appId}&token={token}&start={times}000000&end={times}235959'  -H 'content-type: multipart/form-data;charset=UTF-8'  -F 'file=@{path}'"
    UPLOADCMD = "curl -X POST  'http://api.rhino.datastory.com.cn/external/job/create?appId={appId}&token={token}&{times}'  -H 'content-type: multipart/form-data;charset=UTF-8'  -F 'file=@{path}'"
    #UPLOADCMD = "curl -X POST  'http://api.rhino.datastory.com.cn/external/job/create?appId={appId}&token={token}&start={times}000000&end={times}235959'  -H 'content-type: application/x-www-form-urlencoded;charset=UTF-8'  --data-urlencode 'seeds={seeds}'"
    CHECHCMD = "curl -X GET 'http://api.rhino.datastory.com.cn/external/job/status?appId={appId}&jobId={jobId}&token={token}'"
    #DOWNLOADCMD = "curl -o  {path} 'http://dl.rhino.datastory.com.cn/external/job/dl/external/job/dl?token={token}&appId={appId}&jobId={jobId}'"
    DOWNLOADCMD = 'wget -P {path}  "http://dl.rhino.datastory.com.cn/external/job/dl/external/job/dl?token={token}&appId={appId}&jobId={jobId}"' 
    RETRYTIMES = 5
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self, info):
        self.token = info.token
        self.appid = info.appid
        self.taskname = info.taskname
        self.jobid = ''
        #self.times = time.strftime('%Y%m%d',time.localtime())
        ts = 'start={start}000000&end={end}235959'
        t1 = time.strftime('%Y%m%d', time.localtime(time.time()-60*60*24*1))
        t2 = time.strftime('%Y%m%d', time.localtime(time.time()-60*60*24*8))
        if int(self.appid) == 180:
            self.times = ts.format(start=t2, end=t1)
        else: 
            self.times = ts.format(start=t1, end=t1)
        self.download_path = Storage.getstoragelocation(const.SPIDER_WAIBU_TEMP_PATH)
            
    ################################################################################################################
    # @functions：upload
    # @param： upload file path
    # @return：True if upload successfully, False if too many files have uploaded
    # @note：upload file to Tencent download platform
    ################################################################################################################ 
    def upload(self,upfile):
        cmd = self.UPLOADCMD.format(appId=self.appid, token=self.token, times=self.times, path=upfile)
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            Logger.getlogging().debug(cmd)
            self.jobid = 'test'
            return True            
        exedata = self.execute(cmd)
        code = exedata.get('code',0)
        if int(code) == 1:
            self.jobid = exedata['jobId']
            return True
        secs = 5
        for count in range(0, self.RETRYTIMES):
            time.sleep(secs)
            secs *= 2
            exedata = self.execute(cmd)
            code = exedata.get('code',0)
            if int(code) == 1:
                self.jobid = jsondata['jobId']
                return True
        else:
            param = NotifyParam()
            param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
            param.message = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT.format(
                file=upfile, taskid=self.appid)
            SpiderNotify.notify(param)
            return False 
        
    ################################################################################################################
    # @functions：checkstatus
    # @param:
    # @return：True if upload successfully, False if too many files have uploaded
    # @note：check download status
    ################################################################################################################         
    def checkstatus(self):
        cmd = self.CHECHCMD.format(appId=self.appid, jobId=self.jobid, token=self.token)
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            Logger.getlogging().debug(cmd)
            return True            
        exedata = self.execute(cmd)
        code = exedata.get('code',0)
        status = exedata.get('status','')
        Logger.getlogging().debug('checking code:{code} status:{status}'.format(code=code,status=status))
        if int(code) == 1 and status == 'exported':
            return True     
        else:
            return False 
        
    ################################################################################################################
    # @functions：download
    # @param:
    # @return：
    # @note：
    ################################################################################################################         
    def download(self):
        files = []
        if self.__download__():
            Logger.getlogging().debug(self.download_path)
            time.sleep(3)
            dfiles = FileUtility.getfilelist(self.download_path, [])
            for dfile in dfiles:
                if self.taskname in dfile:
                    files.append(dfile)
        return files
    
    ################################################################################################################
    # @functions：__download__
    # @param： 
    # @return：True if upload successfully, False if too many files have uploaded
    # @note：
    ################################################################################################################         
    def __download__(self):
        cmd = self.DOWNLOADCMD.format(path=self.download_path, appId=self.appid, jobId=self.jobid, token=self.token)
        if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
            Logger.getlogging().debug(cmd)
            return True           
        if self.execute2(cmd):
            return True
        secs = 5
        for count in range(0, self.RETRYTIMES):
            time.sleep(secs)
            secs *= 2
            if self.execute2(cmd):
                return True
        else:
            param = NotifyParam()
            param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
            param.message = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT.format(
                file=FileUtility.getfilename(self.download_path), taskid=self.jobid)
            SpiderNotify.notify(param)
            return False
          
    ################################################################################################################
    # @functions：execute
    # @param： command
    # @return：none
    # @note：execute command
    ################################################################################################################
    def execute(self, cmd, ):
        Logger.getlogging().info('Execute command:{cmd}'.format(cmd=cmd))
        subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subp.wait()
        c = subp.stdout.readline()
        try:
            Logger.getlogging().info(str(c))
            d = json.loads(c)
            return d
        except:
            e = subp.stderr.readline()
            while e:
                if subp.returncode != 0:
                    Logger.getlogging().error(e.strip())
                else:
                    Logger.getlogging().info(e.strip())
                e = subp.stderr.readline()
            return {}
   
 
    def execute2(self, cmd):
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
                
########################################################################
class WaibiDownloaderInfo:
    def __init__(self):
        self.taskname = ''
        self.token = ''
        self.appid = ''
        
if __name__ == '__main__':
    pass
