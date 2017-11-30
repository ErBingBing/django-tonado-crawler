# coding=utf-8
################################################################################################################
# @file: spider.py
# @author: Jiang Siwei
# @date:  2017/07/29 
# @version: Ver1.0.0.0
# @note:
################################################################################################################
import os
import sys
import time
import codecs
from configuration import constant
from configuration.constant import const
from configuration.environment.configure import SpiderConfigure
from controller.downloader import Downloader

from log.spiderlog import Logger
from log.spidernotify import SpiderNotify, NotifyParam
from storage.storage import Storage
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility
from storage.urlmanager import URLManager, URLContext
from configuration.constant import SPIDER_CHANNEL_S1, REQUEST_TYPE_WEBKIT
from utility.common import Common
from dao.sqldao import SQLDAO 
from storage.newsstorage import NewsStorage
from storage.querystorage import QueryStorage
#from tencentplatform.waibudownloader import WaibiDownloader
from controller.downloader import WDownloader 
if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
    from test.etlcontrollermock import ETLController
else:
    from controller.etlcontroller import ETLController

################################################################################################################
# @class：Spider
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Spider:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：Spider初始化内部变量
    ################################################################################################################
    def __init__(self):
        # 下载平台
        SQLDAO.getinstance()
        self.downloader = Downloader()
        self.wdownloader = WDownloader()
        # ETL controller
        self.etl = ETLController()
        self.waitingperiod = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_WAITING_PERIOD))
        self.timeout = int(2*int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_WAIT_PLATFORM_TIMEOUT)))
        self.spiderstarttime = int(time.time())
        self.waibutimeout = 2*60*60
                                                                     
    ################################################################################################################
    # @functions：run
    # @param： none
    # @return：none
    # @note：S1、S2处理逻辑
    ################################################################################################################
    def run(self):
        Logger.getlogging().info('Spider start...')
        if self.istimeout():
            Logger.getlogging().warning('Spider timeout for %s, stop' % constant.SPIDER_RUN_TIMEOUT_HOUR)
            sys.exit(-1)
        SpiderConfigure.getinstance().starttime()
        # 删除临时文件
        Storage.removecachefile()
        Storage.mkcachedir()      
        self.etl.updatedb()      
        #query数据库中的记录更新
        if SpiderConfigure.ismaster():        
            self.etl.storagequery()
    
        if SpiderConfigure.iswaibu():
            #外部数据
            self.waibuetl() 
        else:
            #本地数据
            self.localetl()
        #导出urls生成本地文件
        self.etl.dumpurls()
        self.upload()
        self.loop()
        
        if SpiderConfigure.iswaibu():
            #外部数据刷新
            self.etl.wb_updatedb()
        NewsStorage.show()
        # push result files
        # self.pushfiles()
        # 删除临时文件
        Storage.removecachefile()
        # FINISH
        Logger.getlogging().info('FINISH')

    def localetl(self):
        s1file = SpiderConfigure.getinstance().gets1file()
        self.etl.s1upload(s1file)          
        s2file = self.etl.getqueryfromdb()
        self.etl.s2upload(s2file)
        s3file = self.etl.gettiebaqueryfromdb()
        self.etl.s3upload(s3file)
        self.upload()
        self.loop()

    #----------------------------------------------------------------------
    def loop(self):
        # 循环URL，包括S1以及S2
        continueflag = True
        while continueflag:
            downloadfiles = []
            while True:
                # check time out
                if self.istimeout():
                    param = NotifyParam()
                    param.code = NotifyParam.SPIDER_NOTIFY_TIMEOUT
                    param.message = 'Spider timeout for %s o\'clock, stop' % constant.SPIDER_RUN_TIMEOUT_HOUR
                    SpiderNotify.notify(param)
                    continueflag = False
                    break
                if self.downloader.iscompleted():
                    continueflag = False
                    break
                try:
                    downloadfiles = self.downloader.download()
                    self.upload()
                    if len(downloadfiles) > 0:
                        break
                    else:
                        Logger.getlogging().info('sleeping {0}s......'.format(self.waitingperiod))
                        time.sleep(self.waitingperiod)
                except:
                    Logger.printexception()

            for dfile in downloadfiles:
                starttime = TimeUtility.getcurrentdate(TimeUtility.TIME_FORMAT_DEFAULT)
                self.etl.processfile(dfile)
                logstring = 'PROCESSFILE:\t{file}\t{start}\t{end}'.format(file=FileUtility.getfilename(dfile),
                                                                          start=starttime, 
                                                                          end=TimeUtility.getcurrentdate())
                Logger.getlogging().info(logstring)
                if self.istimeout():
                    param = NotifyParam()
                    param.code = NotifyParam.SPIDER_NOTIFY_TIMEOUT
                    param.message = 'Spider timeout for %s o\'clock, stop' % constant.SPIDER_RUN_TIMEOUT_HOUR
                    SpiderNotify.notify(param)
                    continueflag = False
                    break
                self.upload()
                
    ################################################################################################################
    # @functions：waibuscheduler
    # @param： None
    # @return：None
    # @note：waibuscheduler外部数据调度与下载
    ################################################################################################################      
    def waibuetl(self):
        waibubackup = SpiderConfigure.getwaibubaup()
        if not FileUtility.exists(waibubackup):
            FileUtility.mkdirs(waibubackup) 
            
        waibufile = self.etl.getqueryfromdb()
        if not FileUtility.exists(waibufile):
            Logger.getlogging().warning('{waibufile} not generate!'.format(waibufile=waibufile))
            return
        
        outtime = 0
        self.wdownloader.upload(waibufile)
        continueflag = True
        while continueflag:
            downloadfiles = []
            while True:
                Logger.getlogging().info('sleeping {sec}s......'.format(sec=self.waitingperiod))
                #time.sleep(self.waitingperiod)
                outtime += self.waitingperiod              
                if self.wdownloader.iscompleted():
                    continueflag = False
                    break
                try:
                    downloadfiles = self.wdownloader.download()
                    if downloadfiles:
                        break
                except:
                    Logger.printexception()
                if outtime >= self.waibutimeout:
                    Logger.getlogging().warning('Waibu Data Download Timeout! Spending {sec}s'.format(sec=outtime))
                    continueflag = False
                    break                    
            for dfile in downloadfiles:
                starttime = TimeUtility.getcurrentdate(TimeUtility.TIME_FORMAT_DEFAULT)
                self.etl.wb_analysis(dfile)
                #if FileUtility.exists(waibubackup+FileUtility.getfilename(dfile)):
                    #FileUtility.remove(waibubackup+FileUtility.getfilename(dfile))                
                FileUtility.move(dfile, waibubackup)
                logstring = 'PROCESSWAIBUFILE:\t{file}\t{start}\t{end}'.format(file=FileUtility.getfilename(dfile),
                                                                               start=starttime, 
                                                                               end=TimeUtility.getcurrentdate())
                Logger.getlogging().info(logstring)
                if outtime >= self.waibutimeout:
                    Logger.getlogging().warning('Waibu Data Download Timeout! Spending {sec}s'.format(sec=outtime))
                    continueflag = False
                    break                  
            
    ################################################################################################################
    # @functions：upload
    # @param： none
    # @return：none
    # @note：上传文件到下载平台,
    ################################################################################################################
    def upload(self):
        FileUtility.flush()
        upfiles = FileUtility.getfilelist(Storage.getstoragelocation(const.SPIDER_URLS_TEMP_PATH), [])  
        return self.downloader.upload(upfiles)

    ################################################################################################################
    # @functions：istimeout
    # @param： none
    # @return：True if timeout else False
    # @note：check timeout
    ################################################################################################################
    def istimeout(self):
        #return False
        lt = time.localtime()
        arr = constant.SPIDER_RUN_TIMEOUT_HOUR.split(':')
        hour = int(arr[0])
        minute = 0
        if len(arr) > 1:
            minute = int(arr[1])
        to = False
        if lt.tm_hour > hour:
            to = True
        elif lt.tm_hour == hour:
            if lt.tm_min > minute:
                to = True
        return to

def usage():
    print 'spider.py usage:'
    print '-h,--help: print help message.'
    print '-v, --version: print script version'
    print '-i, --input: input path'


def version():
    print 'spider.py 0.0.100'


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    reload(sys)
    Logger.getlogging().info('Set default encoding to {charset}!'.format(charset=constant.CHARSET_UTF8))
    sys.setdefaultencoding(constant.CHARSET_UTF8)
    spider = Spider()
    try:
        spider.run()
    except:
        Logger.printexception()
    
