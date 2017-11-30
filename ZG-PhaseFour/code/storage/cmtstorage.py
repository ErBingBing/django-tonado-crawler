# -*- coding: utf-8 -*-

"""
# @file: cmtstorage.py
# @author: Jiang Siwei
# @date:  2017/6/7 16:09
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
from newsstorage import NewsStorage
from utility.common import Common
from utility.fileutil import FileUtility
from configuration.constant import CHARSET_UTF8
from configuration.environment.configure import SpiderConfigure 
from utility.timeutility import TimeUtility 

class CMTStorage:
    COMMENTS_FORMAT = u'{channel}\t{content}\t{cmtnum}\t{publishdate}\t{user}\t{url}\t{title}'
    __cidset = set()
    __lastpublish = {}

    @staticmethod
    def storecmt(url, content, pubdate, user):
        content = Common.strfilter(content)
        user = Common.strfilter(user)
        pubdate = TimeUtility.getuniformtime(pubdate)
        if not CMTStorage.exist(url, content, pubdate, user):
            Logger.getlogging().debug('url:{url}, content:{content}, pubdate:{pubdate}, user:{user}'.format(url = url, content=content, pubdate=pubdate, user=user))            
            id = CMTStorage.getid(url, content, pubdate, user)        
            data = {SQLDAO.SPIDER_TABLE_COMMENTS_ID: id,
                    SQLDAO.SPIDER_TABLE_COMMENTS_URL: url,
                    SQLDAO.SPIDER_TABLE_COMMENTS_PUBLISH_DATE: pubdate,
                    SQLDAO.SPIDER_TABLE_COMMENTS_USER: user,
                    SQLDAO.SPIDER_TABLE_COMMENTS_CONTENT: content,
                    SQLDAO.SPIDER_TABLE_COMMENTS_CREATE_DATE: SpiderConfigure.getinstance().starttime() 
                    }
            SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_COMMENTS, SQLDAO.SPIDER_TABLE_COMMENTS_KEYS, SQLDAO.getvaluesfromkeys(data, SQLDAO.SPIDER_TABLE_COMMENTS_KEYS))
    


    @staticmethod
    def exist(url, content, pubdate, user):
        content = Common.strfilter(content)
        user = Common.strfilter(user)
        pubdate = TimeUtility.getuniformtime(pubdate)
        id = CMTStorage.getid(url, content, pubdate, user)
        if id in CMTStorage.__cidset:
            return True
        if SQLDAO.getinstance().exists(SQLDAO.SPIDER_TABLE_COMMENTS,
                                       {SQLDAO.SPIDER_TABLE_COMMENTS_ID: id}):
            CMTStorage.__cidset.add(id)
            return True
        return False

    @staticmethod
    def getcount(url, before=False):
        if not before:
            return SQLDAO.getinstance().count(SQLDAO.SPIDER_TABLE_COMMENTS,
                                              {SQLDAO.SPIDER_TABLE_COMMENTS_URL: url})
        else:
            wheref='{urlkey}=\"{url}\" and {datekey}<={date}'
            where = wheref.format(urlkey=SQLDAO.SPIDER_TABLE_COMMENTS_URL, url=url,
                                  datekey=SQLDAO.SPIDER_TABLE_COMMENTS_CREATE_DATE, date=SQLDAO.gettime())
            return SQLDAO.getinstance().count(SQLDAO.SPIDER_TABLE_COMMENTS,
                                              where=where)
    @staticmethod
    def getlastpublish(url, before=True):
        if not before:
            wheref='{urlkey}=\"{url}\"'
            where = wheref.format(urlkey=SQLDAO.SPIDER_TABLE_COMMENTS_URL, url=url)
        else:
            wheref='{urlkey}=\"{url}\" and {datekey} < {date}'
            where = wheref.format(urlkey=SQLDAO.SPIDER_TABLE_COMMENTS_URL, url=url,
                                  datekey=SQLDAO.SPIDER_TABLE_COMMENTS_CREATE_DATE, date=SpiderConfigure.getinstance().starttime())
        sqlf = 'SELECT MAX({key}) FROM {table} WHERE {where}'
        sql = sqlf.format(key=SQLDAO.SPIDER_TABLE_COMMENTS_PUBLISH_DATE,
                          table=SQLDAO.SPIDER_TABLE_COMMENTS,
                          where=where)
        results = SQLDAO.getinstance().execute(sql, find=True)
        if results[0][0]:
            return results[0][0]
        return TimeUtility.getintformtime(0)
        
    @staticmethod
    def getid(url, content, pubdate, user):
        content = Common.strfilter(content)
        user = Common.strfilter(user)
        pubdate = TimeUtility.getuniformtime(pubdate)
        return Common.md5(Common.urlenc(url) + Common.urlenc(content) + pubdate + Common.urlenc(user))

    @staticmethod
    def writetofile(filename, cond={}):
        Logger.getlogging().debug('Now {t}, Starting Output Comments To {f}'.format(t=int(time.time()),f=filename))
        for doc in SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_COMMENTS, cond):
            url = doc[SQLDAO.SPIDER_TABLE_COMMENTS_URL]
            fstring = CMTStorage.COMMENTS_FORMAT.format(channel=ChannelDao.getchannel(url),
                                                        content=doc[SQLDAO.SPIDER_TABLE_COMMENTS_CONTENT],
                                                        cmtnum=CMTStorage.getcount(url),
                                                        publishdate=doc[SQLDAO.SPIDER_TABLE_COMMENTS_PUBLISH_DATE],
                                                        user=doc[SQLDAO.SPIDER_TABLE_COMMENTS_USER],
                                                        url=doc[SQLDAO.SPIDER_TABLE_COMMENTS_URL],
                                                        title=NewsStorage.gettitle(url))
            FileUtility.writeline(filename, fstring.encode(CHARSET_UTF8))
        FileUtility.flush()
        Logger.getlogging().debug('{t} Comments Finish'.format(t=int(time.time())))
 
if __name__ == '__main__':
    #start = SQLDAO.gettime()
    #filename = './data/output/{start}.txt'.format(start=start)
    #CMTStorage.writetofile(filename)
    #url='http://www.sohu.com/'
    #CMTStorage.storecmt(url, 'content', '2017', 'user')
    #url = 'http://tv.sohu.com/20170906/n600142632.shtml?_f=index_cpc_0_0'
    url = 'http://tv.sohu.com/20170906/n600142632.shtml?_f=index_cpc_0_0'
    print CMTStorage.getlastpublish(url, True)
