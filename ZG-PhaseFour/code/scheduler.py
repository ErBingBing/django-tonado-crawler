# -*- coding: utf-8 -*-
################################################################################################################
# @file: scheduler.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import time

from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from storage.storage import Storage
from utility import const
from utility.fileutil import FileUtility
from controller.downloader import SchedulDownloader

################################################################################################################
# @class：Scheduler
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Scheduler:

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：Spider初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.downloader = SchedulDownloader()
        self.urlpath = SpiderConfigure.getconfig(const.SPIDER_SCHEDULER_DOMAIN, const.SCHEDULER_URL_PATH)
        FileUtility.mkdirs(self.urlpath)
        
    ################################################################################################################
    # @functions：run
    # @param： none
    # @return：none
    # @note：Spider初始化内部变量
    ################################################################################################################
    def run(self):
        while True:
            self.upload()
            self.downloader.download()


    ################################################################################################################
    # @functions：upload
    # @param： none
    # @return：success or not
    # @note：上传成功失败
    ################################################################################################################
    def upload(self):
        upfiles = FileUtility.getfilelist(SpiderConfigure.getconfig(const.SPIDER_SCHEDULER_DOMAIN, const.SCHEDULER_URL_PATH), [])
        donefiles = [dfile for dfile in upfiles if dfile.endswith(constant.POST_FILE_SUFFIX)]
        return self.downloader.upload(donefiles)


if __name__ == '__main__':
    Scheduler().run()
