# -*- coding: utf-8 -*-

"""
# @file: querystorage.py
# @author: Jiang Siwei
# @date:  2017/8/28 16:09
# @version: Ver0.0.0.100
# @note:
"""
#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())

import time
import datetime
#from dao.channeldao import ChannelDao
from dao.sqldao import SQLDAO
from log.spiderlog import Logger
from utility import const
from newsstorage import NewsStorage
from utility.common import Common
from utility.fileutil import FileUtility
from configuration.constant import CHARSET_UTF8
from configuration.environment.configure import SpiderConfigure 
from utility.timeutility import TimeUtility 
########################################################################
class QueryStorage:
    MACHINEFLIST = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN ,const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST)
    MACHINEFLAGLIST = [item.replace('.','') for item in MACHINEFLIST.split(',')]
    
    MACHINEFLIST_WAIBU = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN ,const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST_WAIBU)
    MACHINEFLAGLIST_WAIBU = [item.replace('.','') for item in MACHINEFLIST_WAIBU.split(',')]
    
    MACHINEFLIST_TIEBA = SpiderConfigure.getconfig(const.SPIDER_TENCENT_PLATFORM_DOMAIN ,const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST_TIEBA)
    MACHINEFLAGLIST_TIEBA = [item.replace('.','') for item in MACHINEFLIST_TIEBA.split(',')]
    
    LOCALMACHINEFLAG = SpiderConfigure.getinstance().localmachineflag()
    LOCALQUERYPATH = './data/temp/query/query.txt'
    __instance = None
    __querys   = None
    __querys_tieba = None
    #----------------------------------------------------------------------
    def __init__(self):
        self.querystorage = {}
        self.querystorage_waibu = {}
        self.querystorage_tieba = {}
        for machine in QueryStorage.MACHINEFLAGLIST:
            self.querystorage[machine] = 0
        for machine in QueryStorage.MACHINEFLAGLIST_WAIBU:
            self.querystorage_waibu[machine] = 0     
        for machine in QueryStorage.MACHINEFLAGLIST_TIEBA:
            self.querystorage_tieba[machine] = 0             
    #----------------------------------------------------------------------
    @staticmethod
    def getinstance():
        if not QueryStorage.__instance:
            QueryStorage.__instance = QueryStorage()
        return QueryStorage.__instance
    
    #----------------------------------------------------------------------   
    @staticmethod
    def updatedb():
        for matchine in QueryStorage.MACHINEFLAGLIST:
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS,
                                        where={SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: matchine,
                                               SQLDAO.SPIDER_TABLE_QUERYS_VALID: 1},
                                        update={SQLDAO.SPIDER_TABLE_QUERYS_VALID: 0})
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS_TIEBA,
                                        where={SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: matchine,
                                               SQLDAO.SPIDER_TABLE_QUERYS_VALID: 1},
                                        update={SQLDAO.SPIDER_TABLE_QUERYS_VALID: 0})
        for matchine in QueryStorage.MACHINEFLAGLIST_WAIBU:
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS,
                                        where={SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: matchine,
                                               SQLDAO.SPIDER_TABLE_QUERYS_VALID: 1},
                                        update={SQLDAO.SPIDER_TABLE_QUERYS_VALID: 0})
            
    #----------------------------------------------------------------------
    def storequery(self, query, machineflaglist=MACHINEFLAGLIST):
        #查询query是否存在，如果存在则更新当前updatetime
        #                  如果不存在则查找具有query数量最小的机器,进行query存储
        query = query.strip()
        result = QueryStorage.find(query, machineflaglist)
        if result:
            resultdict = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_QUERYS_KEYS, result)
            machine = resultdict[SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG]
            id = QueryStorage.getid(query, machine)
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS,
                                        {SQLDAO.SPIDER_TABLE_QUERYS_ID: id},
                                        {SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                                         SQLDAO.SPIDER_TABLE_QUERYS_VALID: 1})
        else:
            machine = min(self.querystorage.iteritems(), key=lambda x:x[1])[0]
            data = {SQLDAO.SPIDER_TABLE_QUERYS_ID: QueryStorage.getid(query,machine),
                    SQLDAO.SPIDER_TABLE_QUERYS_QUERY: query,
                    SQLDAO.SPIDER_TABLE_QUERYS_CREATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: machine,
                    SQLDAO.SPIDER_TABLE_QUERYS_VALID: 1}
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_QUERYS, SQLDAO.SPIDER_TABLE_QUERYS_KEYS,
                                        SQLDAO.getvaluesfromkeys(data, SQLDAO.SPIDER_TABLE_QUERYS_KEYS))
        #对各machine的实时存储记录    
        self.querystorage[machine] = self.querystorage.get(machine, 0) + 1
    #----------------------------------------------------------------------
    def storewaibuquery(self, query, machineflaglist=MACHINEFLAGLIST_WAIBU):
        #查询query是否存在，如果存在则更新当前updatetime
        #                  如果不存在则查找具有query数量最小的机器,进行query存储
        query = query.strip()
        result = QueryStorage.find(query, machineflaglist)
        if result:
            resultdict = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_QUERYS_KEYS, result)
            machine = resultdict[SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG]
            id = QueryStorage.getid(query, machine)
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS,
                                        {SQLDAO.SPIDER_TABLE_QUERYS_ID: id},
                                        {SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                                         SQLDAO.SPIDER_TABLE_QUERYS_VALID:1})
        else:
            machine = min(self.querystorage_waibu.iteritems(), key=lambda x:x[1])[0]
            data = {SQLDAO.SPIDER_TABLE_QUERYS_ID: QueryStorage.getid(query,machine),
                    SQLDAO.SPIDER_TABLE_QUERYS_QUERY: query,
                    SQLDAO.SPIDER_TABLE_QUERYS_CREATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: machine,
                    SQLDAO.SPIDER_TABLE_QUERYS_VALID:1}
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_QUERYS, SQLDAO.SPIDER_TABLE_QUERYS_KEYS,
                                        SQLDAO.getvaluesfromkeys(data, SQLDAO.SPIDER_TABLE_QUERYS_KEYS))
        #对各machine的实时存储记录    
        self.querystorage_waibu[machine] = self.querystorage_waibu.get(machine, 0) + 1
    #----------------------------------------------------------------------
    def storetiebaquery(self, query, queryurl, machineflaglist=MACHINEFLAGLIST_TIEBA):
        #查询query是否存在，如果存在则更新当前updatetime
        #                  如果不存在则查找具有query数量最小的机器,进行query存储
        query = query.strip()
        queryurl = queryurl.strip()
        result = QueryStorage.find(query, machineflaglist, table=SQLDAO.SPIDER_TABLE_QUERYS_TIEBA)
        if result:
            resultdict = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_QUERYS_KEYS, result)
            machine = resultdict[SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG]
            id = QueryStorage.getid(query, machine)
            SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_QUERYS_TIEBA,
                                        {SQLDAO.SPIDER_TABLE_QUERYS_ID: id},
                                        {SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                                         SQLDAO.SPIDER_TABLE_QUERYS_VALID:1})
        else:
            machine = min(self.querystorage_tieba.iteritems(), key=lambda x:x[1])[0]
            data = {SQLDAO.SPIDER_TABLE_QUERYS_ID: QueryStorage.getid(query,machine),
                    SQLDAO.SPIDER_TABLE_QUERYS_QUERY: query,
                    SQLDAO.SPIDER_TABLE_QUERYS_CREATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_UPDATEDATE: SpiderConfigure.getinstance().starttime(),
                    SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: machine,
                    SQLDAO.SPIDER_TABLE_QUERYS_QUERYURL:queryurl,
                    SQLDAO.SPIDER_TABLE_QUERYS_VALID:1}
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_QUERYS_TIEBA, SQLDAO.SPIDER_TABLE_QUERYS_KEYS,
                                        SQLDAO.getvaluesfromkeys(data, SQLDAO.SPIDER_TABLE_QUERYS_KEYS))
        #对各machine的实时存储记录    
        self.querystorage_tieba[machine] = self.querystorage_tieba.get(machine, 0) + 1        
    #----------------------------------------------------------------------
    @staticmethod
    def find(query, machineflaglist=MACHINEFLAGLIST, table=SQLDAO.SPIDER_TABLE_QUERYS):
        wheref = '{querykey}=\"{query}\" and {machikey} in ({machine})'
        where  = wheref.format(querykey=SQLDAO.SPIDER_TABLE_QUERYS_QUERY, 
                               query=query,
                               machikey=SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG, 
                               machine=','.join(machineflaglist))
        return SQLDAO.getinstance().find(table, where, multi=False)
    
    @staticmethod
    #----------------------------------------------------------------------
    def getid(query, machine):
        return Common.md5(Common.urlenc(query)+machine)   
    
    #本地数据和外部数据的query
    #----------------------------------------------------------------------
    @staticmethod
    def dumplocalquerys(queryfile=LOCALQUERYPATH, localmachine=LOCALMACHINEFLAG):
        #todaymid = time.mktime(time.strptime(TimeUtility.getcurrentdate(), TimeUtility.DATE_FORMAT_DEFAULT))
        where = {SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: localmachine,
                 SQLDAO.SPIDER_TABLE_QUERYS_VALID:1}
        results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_QUERYS, where, 
                                            keys=[SQLDAO.SPIDER_TABLE_QUERYS_QUERY])
        querys = [''.join(item) for item in results]
        with open(queryfile, 'w+') as fp:
            fp.write('\n'.join(querys))
        return querys
        
    #----------------------------------------------------------------------
    @staticmethod
    def getlocalquerys(queryfile=LOCALQUERYPATH, localmachine=LOCALMACHINEFLAG):
        if not QueryStorage.__querys:
            QueryStorage.__querys = QueryStorage.dumplocalquerys(queryfile, localmachine)
        return QueryStorage.__querys
                                
    #百度贴吧 
    #----------------------------------------------------------------------
    @staticmethod
    def dumplocalquerys_tieba(queryfile=LOCALQUERYPATH, localmachine=LOCALMACHINEFLAG):
        where = {SQLDAO.SPIDER_TABLE_QUERYS_MACHINEFLAG: localmachine,
                 SQLDAO.SPIDER_TABLE_QUERYS_VALID:1}
        results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_QUERYS_TIEBA, where,
                                            keys=[SQLDAO.SPIDER_TABLE_QUERYS_QUERY, SQLDAO.SPIDER_TABLE_QUERYS_QUERYURL])
        querys = ['\t'.join(item) for item in results]
        with open(queryfile, 'w+') as fp:
            fp.write('\n'.join(querys))
        return querys        
    
    #----------------------------------------------------------------------
    @staticmethod
    def getlocalquerys_tieba(queryfile=LOCALQUERYPATH, localmachine=LOCALMACHINEFLAG):
        if not QueryStorage.__querys_tieba:
            QueryStorage.__querys_tieba = QueryStorage.dumplocalquerys_tieba(queryfile, localmachine)
        return QueryStorage.__querys_tieba    
    
    