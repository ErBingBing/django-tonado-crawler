# coding=utf-8
################################################################################################################
# @file: statistics.py
# @author: Sun Xinghua
# @date:  2016/12/1 14:05
# @version: Ver0.0.0.100
# @note:
################################################################################################################
from log.spiderlog import Logger
#
#
################################################################################################################
# @class：statistics
# @author：Sun Xinghua
# @date：2016/12/1 14:05
# @note：
################################################################################################################
class StatisticsManagerA:
    STATISTICS_RESPONSE = 'response'
    STATISTICS_REQUEST = 'request'
    statisticsdata = {STATISTICS_RESPONSE: {}, STATISTICS_REQUEST: {}}
    urlstatus = {'all': 0, 'upload': 0, 'download': 0, 'notemplate': 0, 'nosite': 0, 'gotcomments': 0, 'failgotcomment': 0}
#
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：Spider初始化内部变量
    ################################################################################################################
    def __init__(self):
        pass
#
    ################################################################################################################
    # @functions：updaterequest
    # @param： website
    # @param： times
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updaterequest(website, times):
        website = str(website)
        website = website[website.rindex('.')+1:]
        if website in StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_REQUEST]:
            StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_REQUEST][website] += times
        else:
            StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_REQUEST][website] = times
#
    ################################################################################################################
    # @functions：updateresponse
    # @param： website
    # @param： times
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updateresponse(website, times):
        website = str(website)
        website = website[website.rindex('.') + 1:]
        if website in StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_RESPONSE]:
            StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_RESPONSE][website] += times
        else:
            StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_RESPONSE][website] = times
#
    ################################################################################################################
    # @functions：show
    # @param： none
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def show():
        Logger.getlogging().info('##########################################################')
        Logger.getlogging().info('%16s|%16s|%16s' % ('website','request','response'))
        for key in StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_REQUEST].keys():
            rep = 0
            if StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_RESPONSE].has_key(key):
                rep = StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_RESPONSE][key]
            Logger.getlogging().info('%16s|%16d|%16d' % (
                key,
                StatisticsManager.statisticsdata[StatisticsManager.STATISTICS_REQUEST][key],
                rep
            ))
        Logger.getlogging().info('##########################################################')
#
        Logger.getlogging().info(StatisticsManager.urlstatus)
#
    ################################################################################################################
    # @functions：updateall
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updateall(plus):
        StatisticsManager.urlstatus['all'] += plus
#
    ################################################################################################################
    # @functions：updateupload
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updateupload(plus):
        StatisticsManager.urlstatus['upload'] += plus
#
    ################################################################################################################
    # @functions：updatedownload
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updatedownload(plus):
        StatisticsManager.urlstatus['download'] += plus
#
    ################################################################################################################
    # @functions：updatenotemplate
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updatenotemplate(plus):
        StatisticsManager.urlstatus['notemplate'] += plus
#
    ################################################################################################################
    # @functions：updatenosite
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updatenosite(plus):
        StatisticsManager.urlstatus['nosite'] += plus
#
    ################################################################################################################
    # @functions：updategotcomments
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updategotcomments(plus):
        StatisticsManager.urlstatus['gotcomments'] += plus
#
    ################################################################################################################
    # @functions：updatefailgotcomment
    # @param： plus
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def updatefailgotcomment(plus):
        StatisticsManager.urlstatus['failgotcomment'] += plus