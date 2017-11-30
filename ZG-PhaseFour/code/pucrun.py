# -*- coding: utf-8 -*-
###################################################################################################
# @file: pucrun.py
# @author: Jiangsiwei
# @date:  2017/07/29 
# @version: Ver1.0.0.0
# @note:
###################################################################################################
from spider import Spider
from log.spiderlog import Logger
from controller.downloader import Downloader
import time
def pucrun():
    """"""
    i = 1
    while True:
        Logger.getlogging().debug('This is {i}th download PUC files'.format(i=i))
        filelist = Downloader().downloadpuc()
        if not filelist:
            time.sleep(10*60)
        i += 1

if __name__ == '__main__':
    pucrun()
    