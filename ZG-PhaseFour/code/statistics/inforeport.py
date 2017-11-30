# coding=utf-8
################################################################################################################
# @file: inforeport.py
# @author: Sun Xinghua
# @date:  2017/01/05 10:05
# @version: Ver0.0.0.100
# @note:
################################################################################################################
import os
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from log.spidernotify import SpiderNotify, NotifyParam
from utility import const
from utility.common import Common
from utility.fileutil import FileUtility
from utility.timeutility import TimeUtility
#
#
################################################################################################################
# @class：SpiderReport
# @author：Sun Xinghua
# @date：2017/01/05 10:05
# @note：
################################################################################################################
class SpiderReportA:
    URL_UPLOAD = '0'
    URL_DOWNLOAD = '1'
    URL_NO_TEMPLATE = '2'
    URL_NO_SITE = '3'
    URL_WITH_CMT = '4'
    URL_FAILED = '5'
    REPORT_FORMAT = '{ch},{query},{type},{v1},{v2},{v3},{v4},{v5},{v6}'
    S2URL_FORMAT = '{query},{website},{url}'
#
    __instance = None
#
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.reportlist = {}
        self.s2sitereportlist = {}
        self.s2urlfilepath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                       const.SPIDER_S2_QUERY_URLS_FILE).format(
            date=TimeUtility.getcurrentdate())
        FileUtility.remove(self.s2urlfilepath)
        self.totalreport = Report()
        self.totalreport.channel = 'SUM'
        self.s1urls = []
        self.querysitesmap = {}
        self.s2sitenum = 0
        self.s2urlsitemap = {}
#
    ################################################################################################################
    # @functions：update
    # @param： channel or query
    # @param： type
    # @param： key URL_UPLOAD/URL_DOWNLOAD and so on
    # @param： delta
    # @return：none
    # @note：update value
    ################################################################################################################
    @staticmethod
    def update(channelorquery, type, key, delta, url=None):
        # update reportlist
        if channelorquery not in SpiderReport.getinstance().reportlist:
            SpiderReport.getinstance().reportlist[channelorquery] = {}
        r = SpiderReport.getinstance().reportlist[channelorquery]
        if type not in r:
            r[type] = Report()
        if channelorquery != constant.SPIDER_CHANNEL_S1:
            r[type].channel = constant.SPIDER_CHANNEL_S2
            r[type].query = channelorquery
            r[type].type = type
        r[type].values[key] += delta
        # update s2 site report list
        if channelorquery != constant.SPIDER_CHANNEL_S1 and url is not None:
            urlmd5 = Common.md5(url.strip())
            if urlmd5 in SpiderReport.getinstance().s2urlsitemap:
                website = SpiderReport.getinstance().s2urlsitemap[urlmd5]
                SpiderReport.updates2site(channelorquery, website, key, delta)
        # udapte all
        SpiderReport.getinstance().totalreport.values[key] += delta
#
    @staticmethod
    def updates2site(channelorquery, site, key, delta):
        if channelorquery not in SpiderReport.getinstance().s2sitereportlist:
            SpiderReport.getinstance().s2sitereportlist[channelorquery] = {}
        r = SpiderReport.getinstance().s2sitereportlist[channelorquery]
        if site not in r:
            r[site] = Report()
            r[site].channel = constant.SPIDER_CHANNEL_S2
            r[site].query = channelorquery
            r[site].type = site
        r[site].values[key] += delta
#
    ################################################################################################################
    # @functions：getinstance
    # @param： none
    # @return：none
    # @note：instance
    ################################################################################################################
    @staticmethod
    def getinstance():
        if SpiderReport.__instance is None:
            SpiderReport.__instance = SpiderReport()
        return SpiderReport.__instance
#
    ################################################################################################################
    # @functions：flush
    # @param： none
    # @return：none
    # @note：output all data
    ################################################################################################################
    @staticmethod
    def flush():
        # dump s1 download failed url
        SpiderConfigure.getinstance().setchannel(constant.SPIDER_CHANNEL_S1)
        SpiderConfigure.getinstance().setquery('')
        for url in SpiderReport.getinstance().s1urls:
            Logger.log(url, constant.ERRORCODE_FAIL_LOAD_DOWN)
        # dump none url got from website for query
        querynositemap = {}
        for query in SpiderReport.getinstance().querysitesmap.keys():
            querynositemap[query] = 0
            for site in SpiderReport.getinstance().querysitesmap[query]:
                SpiderReport.s2queryurl(query, site, None, True)
                querynositemap[query] += 1
#
        for query in SpiderReport.getinstance().querysitesmap.keys():
            if query in querynositemap:
                SpiderReport.s2queryurl(query, SpiderReport.getinstance().s2sitenum,
                                        SpiderReport.getinstance().s2sitenum - querynositemap[query], True)
            else:
                SpiderReport.s2queryurl(query, SpiderReport.getinstance().s2sitenum,
                                        SpiderReport.getinstance().s2sitenum, True)
#
        # report
        filename = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                             const.SPIDER_INFO_REPORT_FILE).format(
            date=TimeUtility.getcurrentdate())
        FileUtility.remove(filename)
        FileUtility.writeline(filename, SpiderReport.REPORT_FORMAT.format(
            ch='CHANNEL',
            query='QUERY',
            type='TYPE',
            v1='UPLOAD',
            v2='DOWNLOAD',
            v3='NO_TEMPLATE',
            v4='NO_SITE',
            v5='WITH_CMT',
            v6='FAILED'
        ))
        for key in SpiderReport.getinstance().reportlist.keys():
            for type in SpiderReport.getinstance().reportlist[key].keys():
                r = SpiderReport.getinstance().reportlist[key][type]
                FileUtility.writeline(filename, r.tostring())
        for key in SpiderReport.getinstance().s2sitereportlist.keys():
            for type in SpiderReport.getinstance().s2sitereportlist[key].keys():
                r = SpiderReport.getinstance().s2sitereportlist[key][type]
                FileUtility.writeline(filename, r.tostring())
        FileUtility.writeline(filename, SpiderReport.getinstance().totalreport.tostring())
        FileUtility.writeline(filename, SpiderReport.getinstance().totalreport.tostring2())
        FileUtility.flush()
        threshold = float(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN,
                                                    const.SPIDER_FAILED_THRESHOLD))
        rate = SpiderReport.getinstance().totalreport.getsuccess()
        if rate < threshold:
            Logger.getlogging().warning('success rate is lower than threshold')
            param = NotifyParam()
            param.code = NotifyParam.SPIDER_NOTIFY_OVER_FAILED
            param.message = 'success rate {rate} is lower than threshold {th}'.format(rate=Common.float2percent(rate),
                                                                                      th=Common.float2percent(
                                                                                          threshold))
            SpiderNotify.notify(param)
#
    ################################################################################################################
    # @functions：s2queryurl
    # @param： query
    # @param： website
    # @param： url
    # @param： onlywrite
    # @return：none
    # @note：output s2 query result
    ################################################################################################################
    @staticmethod
    def s2queryurl(query, website, url, onlywrite=False):
        sitename = str(website)
        if '.' in sitename:
            sitename = sitename[sitename.rindex('.') + 1:]
        if not onlywrite:
            SpiderReport.removequerysite(query, sitename)
            SpiderReport.getinstance().s2urlsitemap[Common.md5(url.strip())] = sitename
            SpiderReport.updates2site(query, sitename, SpiderReport.URL_UPLOAD, 1)
        FileUtility.writeline(SpiderReport.getinstance().s2urlfilepath, SpiderReport.S2URL_FORMAT.format(
            query=query,
            website=sitename,
            url=url
        ))
#
    ################################################################################################################
    # @functions：puts1url
    # @param： s1 url
    # @return：none
    # @note：add s1 url
    ################################################################################################################
    @staticmethod
    def puts1url(url):
        SpiderReport.getinstance().s1urls.append(url.strip())
#
    ################################################################################################################
    # @functions：removes1url
    # @param： url s1 url
    # @return：none
    # @note：s1 url downloaded successfully
    ################################################################################################################
    @staticmethod
    def removes1url(url):
        try:
            SpiderReport.getinstance().s1urls.remove(url)
        except:
            Logger.getlogging().error('{url} no in s1 list'.format(url=url))
#
    ################################################################################################################
    # @functions：loadquery
    # @param： querylist s2 query list
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def loadquery(querylist):
        for query in querylist:
            SpiderReport.getinstance().querysitesmap[query] = []
#
    ################################################################################################################
    # @functions：loadsites
    # @param： sitelist s2 site list
    # @return：none
    # @note：
    ################################################################################################################
    @staticmethod
    def loadsites(sitelist):
        SpiderReport.getinstance().s2sitenum = len(sitelist)
        for site in sitelist:
            classname = str(site.__class__)
            sitename = classname[classname.rindex('.') + 1:]
            for query in SpiderReport.getinstance().querysitesmap:
                SpiderReport.getinstance().querysitesmap[query].append(sitename)
#
    ################################################################################################################
    # @functions：removequerysite
    # @param： query
    # @param： site
    # @return：none
    # @note：check site for query
    ################################################################################################################
    @staticmethod
    def removequerysite(query, site):
        if query in SpiderReport.getinstance().querysitesmap:
            if site in SpiderReport.getinstance().querysitesmap[query]:
                SpiderReport.getinstance().querysitesmap[query].remove(site)
#
#
################################################################################################################
# @class：Report
# @author：Sun Xinghua
# @date：2017/01/05 10:05
# @note：
################################################################################################################
class Report:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        self.channel = constant.SPIDER_CHANNEL_S1
        self.query = ''
        self.type = ''
        self.values = {SpiderReport.URL_UPLOAD: 0,
                       SpiderReport.URL_DOWNLOAD: 0,
                       SpiderReport.URL_NO_TEMPLATE: 0,
                       SpiderReport.URL_NO_SITE: 0,
                       SpiderReport.URL_WITH_CMT: 0,
                       SpiderReport.URL_FAILED: 0}
#
    ################################################################################################################
    # @functions：tostring
    # @param： none
    # @return：to string
    # @note：初始化内部变量
    ################################################################################################################
    def tostring(self):
        return SpiderReport.REPORT_FORMAT.format(
            ch=self.channel,
            query=self.query,
            type=self.type,
            v1=self.values[SpiderReport.URL_UPLOAD],
            v2=self.values[SpiderReport.URL_DOWNLOAD],
            v3=self.values[SpiderReport.URL_NO_TEMPLATE],
            v4=self.values[SpiderReport.URL_NO_SITE],
            v5=self.values[SpiderReport.URL_WITH_CMT],
            v6=self.values[SpiderReport.URL_FAILED] + self.values[SpiderReport.URL_UPLOAD] - self.values[
                SpiderReport.URL_DOWNLOAD]
        )
#
    ################################################################################################################
    # @functions：tostring2
    # @param： none
    # @return：to string , value to percent
    # @note：
    ################################################################################################################
    def tostring2(self):
        if self.values[SpiderReport.URL_UPLOAD] > 0:
            total = float(self.values[SpiderReport.URL_UPLOAD])
            return SpiderReport.REPORT_FORMAT.format(
                ch=self.channel,
                query=self.query,
                type=self.type,
                v1=Common.float2percent(self.values[SpiderReport.URL_UPLOAD] / total),
                v2=Common.float2percent(self.values[SpiderReport.URL_DOWNLOAD] / total),
                v3=Common.float2percent(self.values[SpiderReport.URL_NO_TEMPLATE] / total),
                v4=Common.float2percent(self.values[SpiderReport.URL_NO_SITE] / total),
                v5=Common.float2percent(self.values[SpiderReport.URL_WITH_CMT] / total),
                v6=Common.float2percent(
                    (self.values[SpiderReport.URL_FAILED] + self.values[SpiderReport.URL_UPLOAD] - self.values[
                        SpiderReport.URL_DOWNLOAD]) / total)
            )
        else:
            return SpiderReport.REPORT_FORMAT.format(
                ch=self.channel,
                query=self.query,
                type=self.type,
                v1=Common.float2percent(0.0),
                v2=Common.float2percent(0.0),
                v3=Common.float2percent(0.0),
                v4=Common.float2percent(0.0),
                v5=Common.float2percent(0.0),
                v6=Common.float2percent(0.0))
#
    ################################################################################################################
    # @functions：getsuccess
    # @param： none
    # @return：success rate
    # @note：
    ################################################################################################################
    def getsuccess(self):
        if self.values[SpiderReport.URL_UPLOAD] > 0:
            total = float(self.values[SpiderReport.URL_UPLOAD])
            return ((self.values[SpiderReport.URL_DOWNLOAD] - self.values[
                SpiderReport.URL_FAILED]) / total)
        else:
            return 0.0
#
#
if __name__ == '__main__':
    os.chdir('..')
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_UPLOAD, 100)
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_DOWNLOAD, 90)
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_NO_SITE, 10)
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_NO_TEMPLATE, 20)
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_WITH_CMT, 30)
    SpiderReport.update(constant.SPIDER_CHANNEL_S1, '', SpiderReport.URL_FAILED, 50)
    SpiderReport.flush()
