# -*- coding: utf-8 -*-
###################################################################################################
# @file: diffcontroller.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note: 
###################################################################################################
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from dao.spiderdao import SpiderDao
from log.spiderlog import Logger

################################################################################################################
# @class：DiffController
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
from utility import const
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility


class DiffController:
    DIFF_FILE_NAME_FORMAT = '{suffix}_{ts}_diff.txt'

    ###################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ###################################################################################################
    def __init__(self):
        self.database = SpiderDao()
        suffix = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                           const.SPIDER_OUTPUT_FILENAME_SUFFIX)
        ts = TimeUtility.getcurrentdate(TimeUtility.TIMESTAMP_FORMAT)
        self.difffile = '{path}/{dt}/{file}'.format(
            path=SpiderConfigure.getinstance().getconfig(const.SPIDER_STORAGE_DOMAIN, const.SPIDER_OUTPUT_PATH),
            dt=TimeUtility.getcurrentdate(),
            file=DiffController.DIFF_FILE_NAME_FORMAT.format(suffix=suffix, ts=ts))

    ###################################################################################################
    # @functions：printdetail
    # @param： none
    # @return：none
    # @note：输出差分信息到日志
    ###################################################################################################
    def show(self):
        diffinfolist = {}
        predict = self.database.getall()
        instances = URLStorage.getinstances()
        Logger.getlogging().info(
            '##############################################################################################')
        Logger.getlogging().info('%8s|%8s|%8s|%8s|%8s|%8s|%8s|%20s|%16s' %
                                 ('key',
                                  'flag',
                                  'cmtnum',
                                  'clicknum',
                                  'votenum',
                                  'fansnum',
                                  'realnum',
                                  'pubtime',
                                  'timestamp'))
        for ins in instances.keys():
            diffinfolist[ins] = DiffInfomation()
            if ins != constant.SPIDER_CHANNEL_S1:
                diffinfolist[ins].channel =  constant.SPIDER_CHANNEL_S2
                diffinfolist[ins].query = ins
            for key in instances[ins].urlinfodict:
                if instances[ins].urlinfodict[key].realnum > 0:
                    StatisticsManager.updategotcomments(1)
                elif instances[ins].urlinfodict[key].cmtnum > 0:
                    StatisticsManager.updatefailgotcomment(1)
                if predict and key in predict:
                    info = URLCommentInfo.fromstring(predict[key])
                    if not instances[ins].urlinfodict[key].isequal(info):
                        self.printinfo(ins, info, '-')
                        self.printinfo(ins, instances[ins].urlinfodict[key], '+')
                        if instances[ins].urlinfodict[key].cmtnum > 0:
                            diffinfolist[ins].deltacmt += self.diff(instances[ins].urlinfodict[key].cmtnum, info.cmtnum)
                        else:
                            diffinfolist[ins].deltacmt += self.diff(instances[ins].urlinfodict[key].realnum,
                                                                    info.realnum)
                        diffinfolist[ins].deltaclick += self.diff(instances[ins].urlinfodict[key].clicknum,
                                                                  info.clicknum)
                        diffinfolist[ins].deltavote += self.diff(instances[ins].urlinfodict[key].votenum, info.votenum)
                        diffinfolist[ins].deltafans += self.diff(instances[ins].urlinfodict[key].fansnum, info.fansnum)
                else:
                    self.printinfo(ins, instances[ins].urlinfodict[key], '+')
                    if instances[ins].urlinfodict[key].cmtnum > 0:
                        diffinfolist[ins].deltacmt += instances[ins].urlinfodict[key].cmtnum
                    else:
                        diffinfolist[ins].deltacmt += max(0, instances[ins].urlinfodict[key].realnum)
                    diffinfolist[ins].deltaclick += max(0, instances[ins].urlinfodict[key].clicknum)
                    diffinfolist[ins].deltavote += max(0, instances[ins].urlinfodict[key].votenum)
                    diffinfolist[ins].deltafans += max(0, instances[ins].urlinfodict[key].fansnum)
        Logger.getlogging().info(
            '##############################################################################################')
        if FileUtility.exists(self.difffile):
            FileUtility.remove(self.difffile)
        for key in diffinfolist.keys():
            Logger.getlogging().info(diffinfolist[key].tostring())
            FileUtility.writeline(self.difffile, diffinfolist[key].tostring())

    ###################################################################################################
    # @functions：printinfo
    # @param： info 信息
    # @param： flag 添加为+ 删除为-
    # @return：none
    # @note：输出差分信息到日志
    ###################################################################################################
    def printinfo(self, key, info, flag):
        Logger.getlogging().info('%8s|%8s|%8s|%8s|%8s|%8s|%8s|%20s|%16s' %
                                 (key,
                                  flag,
                                  str(info.cmtnum if info.cmtnum > 0 else info.realnum),
                                  str(info.clicknum),
                                  str(info.votenum),
                                  str(info.fansnum),
                                  str(info.realnum),
                                  str(info.pubtime),
                                  str(info.timestamp)))

    def diff(self, x, y):
        delta = max(0, x) - max(0, y)
        return max(0, delta)


class DiffInfomation:
    STRING_FORMAT = '{channel}\t{query}\t{cmtnum}\t{clicknum}\t{votenum}\t{fansnum}'

    def __init__(self):
        self.channel = constant.SPIDER_CHANNEL_S1
        self.query = ''
        self.deltacmt = 0
        self.deltaclick = 0
        self.deltavote = 0
        self.deltafans = 0

    def tostring(self):
        return DiffInfomation.STRING_FORMAT.format(channel=self.channel, query=self.query, cmtnum=self.deltacmt,
                                                   clicknum=self.deltaclick, votenum=self.deltavote,
                                                   fansnum=self.deltafans)
