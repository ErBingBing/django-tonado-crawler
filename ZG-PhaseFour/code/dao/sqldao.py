# coding=utf-8
#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())

import MySQLdb
import time
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
from utility import const
from utility.fileutil import FileUtility

########################################################################
class SQLDAO:
    SPIDER_TABLE_QUERYS          = 'querys'
    SPIDER_TABLE_QUERYS_TIEBA    = 'tiebaquerys'
    SPIDER_TABLE_QUERYS_INDEX      = 'id'
    SPIDER_TABLE_QUERYS_ID         = 'id'
    SPIDER_TABLE_QUERYS_QUERY      = 'query'
    SPIDER_TABLE_QUERYS_QUERYURL      = 'queryurl'
    SPIDER_TABLE_QUERYS_CREATEDATE = 'createdate'
    SPIDER_TABLE_QUERYS_UPDATEDATE = 'updatedate'
    SPIDER_TABLE_QUERYS_MACHINEFLAG= 'machineflag'
    SPIDER_TABLE_QUERYS_VALID      = 'valid'
    SPIDER_TABLE_QUERYS_KEY1       = 'key1'
    SPIDER_TABLE_QUERYS_KEY2       = 'key2'
    SPIDER_TABLE_QUERYS_KEY3       = 'key3'
    SPIDER_TABLE_QUERYS_KEY4       = 'key4'    
    SPIDER_TABLE_QUERYS_KEY5       = 'key5'
    SPIDER_TABLE_QUERYS_KEYS       = [SPIDER_TABLE_QUERYS_ID, 
                                      SPIDER_TABLE_QUERYS_QUERY, 
                                      SPIDER_TABLE_QUERYS_QUERYURL,
                                      SPIDER_TABLE_QUERYS_CREATEDATE, 
                                      SPIDER_TABLE_QUERYS_UPDATEDATE, 
                                      SPIDER_TABLE_QUERYS_MACHINEFLAG,
                                      SPIDER_TABLE_QUERYS_VALID,
                                      SPIDER_TABLE_QUERYS_KEY1, SPIDER_TABLE_QUERYS_KEY2, SPIDER_TABLE_QUERYS_KEY3, SPIDER_TABLE_QUERYS_KEY4, SPIDER_TABLE_QUERYS_KEY5]
    
    
    SPIDER_TABLE_NEWS           = 'news'
    SPIDER_TABLE_NEWS_COLD      = 'news_cold'
    SPIDER_TABLE_NEWS_INDEX       = 'id'
    SPIDER_TABLE_NEWS_ID          = 'id'
    SPIDER_TABLE_NEWS_URL         = 'url'
    SPIDER_TABLE_NEWS_QUERY       = 'query'
    SPIDER_TABLE_NEWS_CHANNEL     = 'channel'
    SPIDER_TABLE_NEWS_TYPE        = 'type'
    SPIDER_TABLE_NEWS_MACHINEFLAG = 'machineflag'
    SPIDER_TABLE_NEWS_TITLE       = 'title'
    SPIDER_TABLE_NEWS_BODY        = 'body'
    SPIDER_TABLE_NEWS_PUBLISH_DATE= 'publishdate'
    SPIDER_TABLE_NEWS_CREATE_DATE = 'createdate'
    SPIDER_TABLE_NEWS_UPDATE_DATE = 'updatedate'
    SPIDER_TABLE_NEWS_CMTNUM      = 'cmtnum'
    SPIDER_TABLE_NEWS_CLICKNUM    = 'clicknum'
    SPIDER_TABLE_NEWS_FANSNUM     = 'fansnum'
    SPIDER_TABLE_NEWS_VOTENUM     = 'votenum'
    #'key1'作为是否数据已导出标记
    SPIDER_TABLE_NEWS_KEY1        = 'key1'
    SPIDER_TABLE_NEWS_KEY2        = 'key2'
    SPIDER_TABLE_NEWS_KEY3        = 'key3'
    SPIDER_TABLE_NEWS_KEY4        = 'key4'    
    SPIDER_TABLE_NEWS_KEY5        = 'key5'
    
    SPIDER_TABLE_NEWS_KEYS        = [SPIDER_TABLE_NEWS_ID, 
                                     SPIDER_TABLE_NEWS_QUERY,
                                     SPIDER_TABLE_NEWS_URL,
                                     SPIDER_TABLE_NEWS_TITLE,
                                     SPIDER_TABLE_NEWS_BODY,
                                     SPIDER_TABLE_NEWS_CMTNUM,
                                     SPIDER_TABLE_NEWS_CLICKNUM,
                                     SPIDER_TABLE_NEWS_FANSNUM,
                                     SPIDER_TABLE_NEWS_VOTENUM,
                                     SPIDER_TABLE_NEWS_PUBLISH_DATE,
                                     SPIDER_TABLE_NEWS_CREATE_DATE,
                                     SPIDER_TABLE_NEWS_UPDATE_DATE,                                     
                                     SPIDER_TABLE_NEWS_CHANNEL, 
                                     SPIDER_TABLE_NEWS_TYPE,     
                                     SPIDER_TABLE_NEWS_MACHINEFLAG, 
                                     SPIDER_TABLE_NEWS_KEY1, SPIDER_TABLE_NEWS_KEY2, SPIDER_TABLE_NEWS_KEY3, SPIDER_TABLE_NEWS_KEY4, SPIDER_TABLE_NEWS_KEY5]    
    SPIDER_TABLE_NEWS_KEYS2        = [SPIDER_TABLE_NEWS_ID, 
                                     SPIDER_TABLE_NEWS_URL, 
                                     SPIDER_TABLE_NEWS_QUERY, 
                                     SPIDER_TABLE_NEWS_CHANNEL, 
                                     SPIDER_TABLE_NEWS_TYPE,
                                     SPIDER_TABLE_NEWS_CREATE_DATE,
                                     SPIDER_TABLE_NEWS_MACHINEFLAG]   
    SPIDER_TABLE_NEWS_KEYS3        = [SPIDER_TABLE_NEWS_TITLE,
                                     SPIDER_TABLE_NEWS_BODY,
                                     SPIDER_TABLE_NEWS_PUBLISH_DATE,
                                     SPIDER_TABLE_NEWS_UPDATE_DATE,
                                     SPIDER_TABLE_NEWS_CMTNUM,
                                     SPIDER_TABLE_NEWS_CLICKNUM,
                                     SPIDER_TABLE_NEWS_FANSNUM,
                                     SPIDER_TABLE_NEWS_VOTENUM]
                                       
    SPIDER_TABLE_COMMENTS           = 'comments'
    SPIDER_TABLE_COMMENTS_INDEX        = 'id'
    SPIDER_TABLE_COMMENTS_ID           = 'id'
    SPIDER_TABLE_COMMENTS_URL          = 'url'
    SPIDER_TABLE_COMMENTS_CONTENT      = 'content'
    SPIDER_TABLE_COMMENTS_PUBLISH_DATE = 'publishdate'
    SPIDER_TABLE_COMMENTS_USER         = 'user'
    SPIDER_TABLE_COMMENTS_CREATE_DATE  = 'createdate' 
    #'key1'作为是否数据已导出标记
    SPIDER_TABLE_COMMENTS_KEY1         = 'key1'
    SPIDER_TABLE_COMMENTS_KEY2         = 'key2'
    SPIDER_TABLE_COMMENTS_KEY3         = 'key3'
    SPIDER_TABLE_COMMENTS_KEY4         = 'key4'    
    SPIDER_TABLE_COMMENTS_KEY5         = 'key5'    
    SPIDER_TABLE_COMMENTS_KEYS         = [SPIDER_TABLE_COMMENTS_ID,
                                          SPIDER_TABLE_COMMENTS_URL,
                                          SPIDER_TABLE_COMMENTS_CONTENT,
                                          SPIDER_TABLE_COMMENTS_PUBLISH_DATE,
                                          SPIDER_TABLE_COMMENTS_USER,
                                          SPIDER_TABLE_COMMENTS_CREATE_DATE,
                                          SPIDER_TABLE_COMMENTS_KEY1, SPIDER_TABLE_COMMENTS_KEY2, SPIDER_TABLE_COMMENTS_KEY3, SPIDER_TABLE_COMMENTS_KEY4, SPIDER_TABLE_COMMENTS_KEY5]
    
    #数据库数据类型
    INTFORMAT     = 'BIGINT(15)'
    CHARFORMAT    = 'VARCHAR(500)'
    TEXTFORAT     = 'LONGTEXT'
    DATEFORMAT    = "YYYY-MM-DD HH:MM:SS"

    CREATEDATABASE = 'CREATE DATABASE IF NOT EXISTS {database}'
    CREATETABLE    = 'CREATE TABLE {table} ({keys}, UNIQUE INDEX({index}))'
    CREATEINDEX    = 'CREATE INDEX {index} ON {table}'
    INSERTTABLE    = 'INSERT INTO {table} ({keys}) VALUES ({values})'
    DELETETABLE    = 'DELETE FROM {table} WHERE {where}'
    UPDATETABLE    = 'UPDATE {table} SET {update} WHERE {where}'
    UPDATETABLEALL = 'UPDATE {table} SET {update}'
    SELECTTABLE    = 'SELECT {keys} FROM {table} WHERE {where}'
    SELECTTABLEALL = 'SELECT * FROM {table} WHERE {where}'
    MAX_RETRY_TIMES= 3
    __instance = None
    
    #----------------------------------------------------------------------
    def __init__(self):
        self.database = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_DATABASE)
        self.ip = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_IP)
        self.port = int(SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_PORT))
        self.password = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_PASSWORD)
        self.user = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_USERNAME)
        self.charset = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_CHARSET)
        self.connected = False
        #self.connect = None
        self.retrytime = 0
        self.checktime = SQLDAO.gettime()
        self.createdatabase()

    #----------------------------------------------------------------------    
    @staticmethod
    def getinstance():
        if not SQLDAO.__instance:
            SQLDAO.__instance = SQLDAO()
        return SQLDAO.__instance
    #----------------------------------------------------------------------    
    def check(self):
        if not self.connected:
            return self.connect()
        else:
            if SQLDAO.gettime() - self.checktime > 300:
                self.checktime = SQLDAO.gettime()
                try:
                    self.connect.ping()
                    return True
                except MySQLdb.Error:
                    Logger.getlogging().error('Server not available!')
                    self.close()
                    return self.connect()
            else:
                return True 
    #----------------------------------------------------------------------           
    def connect(self):
        if not self.connected:
            try:
                self.connect = MySQLdb.connect(host=self.ip, port=self.port, user=self.user, passwd=self.password, charset=self.charset)
                self.connected = True
                self.connect.ping()
                return True
            except MySQLdb.Error:
                Logger.getlogging().error('Server not available!')
                self.close()
                return self.connect()
        return True

    #----------------------------------------------------------------------
    def close(self):
        if self.connected:
            self.connect.close()
            self.connected = False
    #----------------------------------------------------------------------
    def execute(self, sql, find=False, retrycount=0):
        if self.check():
            try:
                cur = self.connect.cursor()
                cur.execute(sql)
                if find:
                    results = cur.fetchall()
                cur.close()
                self.connect.commit() 
                if find:
                    return results
                return True
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().error(sql)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.execute(sql, find, retrycount)         
        
    #----------------------------------------------------------------------
    def insert(self, table, keys, values, mutli=False, retrycount=0):
        if self.check():
            sql = SQLDAO.INSERTTABLE.format(table=table, keys=', '.join(keys), values=', '.join(['%s']*len(keys)))
            try:
                cur = self.connect.cursor()
                if not mutli:
                    tempvalues = ['\"{value}\"'.format(value=item) for item in values]
                    Logger.getlogging().debug(sql % tuple(tempvalues)) 
                    cur.execute(sql, tuple(values))
                else:
                    tempvalues = []
                    for value in values:
                        tempvalue = ['\"{value}\"'.format(value=item) for item in value]
                        Logger.getlogging().debug(sql % tuple(tempvalue))
                        tempvalues.append(tuple(value))
                    cur.executemany(sql, tempvalues)
                cur.close()
                self.connect.commit()
                return True
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().error(sql)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.insert(table, keys, values, mutli, retrycount)
    
    #----------------------------------------------------------------------
    def update(self, table, where={}, update={}, relation='and', retrycount=0):
        if self.check():
            updatevalue = ['{key}=\"{value}\"'.format(key=key, value=value) for key, value in update.iteritems()]
            updatevalue=', '.join(updatevalue)
            if where and isinstance(where, dict):
                tempwhere =  [' {key}=\"{value}\" '.format(key=key, value=value)  for key, value in where.iteritems()]
                tempwhere=relation.join(tempwhere)
                sql = SQLDAO.UPDATETABLE.format(table=table,  update=updatevalue, where=tempwhere)
            elif where:
                sql = SQLDAO.UPDATETABLE.format(table=table,  update=updatevalue, where=where)
            else:
                sql = SQLDAO.UPDATETABLEALL.format(table=table, update=updatevalue)
            Logger.getlogging().debug(sql)
            try:
                cur = self.connect.cursor()
                cur.execute(sql)
                cur.close()
                self.connect.commit() 
                return True
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().error(sql)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.update(table, where, update, relation, retrycount)        
      
    #----------------------------------------------------------------------
    def find(self, table, where={}, keys=[], multi=True, many=0, relation='and', retrycount=0):
        if self.check():
            if where and isinstance(where, dict):
                tempwhere =  [' {key}=\"{value}\" '.format(key=key, value=value)  for key, value in where.iteritems()]
                tempwhere = relation.join(tempwhere)
                if not keys:
                    sql = SQLDAO.SELECTTABLEALL.format(table=table, where=tempwhere)
                else:
                    sql = SQLDAO.SELECTTABLE.format(table=table, keys=', '.join(keys), where=tempwhere)
            else:
                if not keys:
                    sql = SQLDAO.SELECTTABLEALL.format(table=table, where=where)   
                else:
                    sql = SQLDAO.SELECTTABLE.format(table=table, keys=', '.join(keys), where=where)                
            #Logger.getlogging().debug(sql)
            try:
                cur = self.connect.cursor()
                cur.execute(sql)
                if multi:
                    results = cur.fetchall()
                elif many:
                    results = cur.fetchmany(many)
                else:
                    results = cur.fetchone()
                cur.close()
                self.connect.commit()                   
                return results
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().error(sql)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.find(table, where, keys, multi, many, relation, retrycount)
        
    #----------------------------------------------------------------------
    def delete(self,table, where, relation='and', retrycount=0):
        if self.check():
            if where and isinstance(where, dict):
                tempwhere =  [' {key}=\"{value}\" '.format(key=key, value=value)  for key, value in where.iteritems()]
                tempwhere='and'.join(tempwhere)
                sql = SQLDAO.DELETETABLE.format(table=table, where=tempwhere)
            else:
                sql = SQLDAO.DELETETABLE.format(table=table, where=where)
            Logger.getlogging().debug(sql)
            try:
                cur = self.connect.cursor()
                cur.execute(sql)
                cur.close()
                self.connect.commit() 
                return True
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().error(sql)
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.delete(table, where, relation, retrycount)              
        
    #----------------------------------------------------------------------
    def exists(self, table, where={}, relation='and'):
        if self.check():
            results = self.find(table, where, relation=relation)
            if results:
                return True
            return False
    #----------------------------------------------------------------------
    def count(self, table, where={}, relation='and'):
        if self.check():
            results = self.find(table, where, relation=relation)
            if results:
                return len(results)
            return 0
    #----------------------------------------------------------------------
    def createdatabase(self):
        sql = SQLDAO.CREATEDATABASE.format(database=self.database)
        #Logger.getlogging().debug(sql)
        if self.check():
            cur = self.connect.cursor()
            cur.execute(sql)
            self.connect.select_db(self.database)
            self.createtable()

    #----------------------------------------------------------------------
    def createtable(self):
        if self.check():
            cur = self.connect.cursor()
            cur.execute('SHOW TABLES')
            tables = cur.fetchall()
            tables = [item[0] for item in tables]
            if SQLDAO.SPIDER_TABLE_QUERYS not in tables:
                sql = SQLDAO.CREATETABLE.format(table=SQLDAO.SPIDER_TABLE_QUERYS, 
                                                keys =SQLDAO.getstring(SQLDAO.SPIDER_TABLE_QUERYS_KEYS),
                                                index=SQLDAO.SPIDER_TABLE_QUERYS_INDEX)
                Logger.getlogging().debug(sql)
                cur.execute(sql)
            if SQLDAO.SPIDER_TABLE_NEWS not in tables:
                sql = SQLDAO.CREATETABLE.format(table=SQLDAO.SPIDER_TABLE_NEWS, 
                                                keys=SQLDAO.getstring(SQLDAO.SPIDER_TABLE_NEWS_KEYS),
                                                index=SQLDAO.SPIDER_TABLE_NEWS_INDEX)
                Logger.getlogging().debug(sql)
                cur.execute(sql)
            if SQLDAO.SPIDER_TABLE_COMMENTS  not in tables:
                sql = SQLDAO.CREATETABLE.format(table=SQLDAO.SPIDER_TABLE_COMMENTS, 
                                                keys=SQLDAO.getstring(SQLDAO.SPIDER_TABLE_COMMENTS_KEYS),
                                                index=SQLDAO.SPIDER_TABLE_COMMENTS_INDEX)
                Logger.getlogging().debug(sql)
                cur.execute(sql)
            if SQLDAO.SPIDER_TABLE_NEWS_COLD not in tables:
                sql = SQLDAO.CREATETABLE.format(table=SQLDAO.SPIDER_TABLE_NEWS_COLD, 
                                                keys=SQLDAO.getstring(SQLDAO.SPIDER_TABLE_NEWS_KEYS),
                                                index=SQLDAO.SPIDER_TABLE_NEWS_INDEX)
                Logger.getlogging().debug(sql)
                cur.execute(sql)
            if SQLDAO.SPIDER_TABLE_QUERYS_TIEBA not in tables:
                sql = SQLDAO.CREATETABLE.format(table=SQLDAO.SPIDER_TABLE_QUERYS_TIEBA , 
                                                keys=SQLDAO.getstring(SQLDAO.SPIDER_TABLE_QUERYS_KEYS),
                                                index=SQLDAO.SPIDER_TABLE_QUERYS_INDEX)
                Logger.getlogging().debug(sql)
                cur.execute(sql)            
            cur.close()
            self.connect.commit()
    
    #----------------------------------------------------------------------  
    @staticmethod
    def getstring(lists):
        string = []
        for item in lists:
            if item == SQLDAO.SPIDER_TABLE_NEWS_INDEX:
                string.append(item + ' ' + 'CHAR(64)')
            elif item == SQLDAO.SPIDER_TABLE_NEWS_CHANNEL or item == SQLDAO.SPIDER_TABLE_NEWS_TYPE:
                string.append(item + ' ' + 'CHAR(3)')
            elif item == SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE:
                string.append(item + ' ' + 'CHAR(19)')
            elif 'date' in item or item == SQLDAO.SPIDER_TABLE_QUERYS_VALID:
                string.append(item + ' ' + 'INT')
            elif 'num' in item:
                string.append(item + ' ' + SQLDAO.INTFORMAT)
            elif item == SQLDAO.SPIDER_TABLE_NEWS_MACHINEFLAG:
                string.append(item + ' ' + 'CHAR(12)')
            elif item == SQLDAO.SPIDER_TABLE_NEWS_BODY or item == SQLDAO.SPIDER_TABLE_COMMENTS_CONTENT:
                string.append(item + ' ' + SQLDAO.TEXTFORAT)
            else:
                string.append(item + ' ' + SQLDAO.CHARFORMAT)
        return ', '.join(string)
    #----------------------------------------------------------------------
    def callproc(self, procname, args, retrycount=0):
        Logger.getlogging().debug(procname)
        if self.check():
            try:
                cur = self.connect.cursor()
                cur.callproc(procname, args)           
                cur.close()
                self.connect.commit()   
            except:
                if retrycount == SQLDAO.MAX_RETRY_TIMES:
                    Logger.getlogging().debug(str(args))
                    Logger.printexception()
                    return False
            retrycount += 1
            return self.callproc(procname, args, retrycount)
    #----------------------------------------------------------------------       
    @staticmethod
    def gettime():
        return int(time.time())
    
    #----------------------------------------------------------------------
    @staticmethod
    def getnulldata():
        return SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, [None]*len(SQLDAO.SPIDER_TABLE_NEWS_KEYS))
    
    @staticmethod
    def getdictdata(keys, values):
        return dict(zip(keys, values))
    #----------------------------------------------------------------------
    @staticmethod
    def getvaluesfromkeys(dictdata, keys=SPIDER_TABLE_NEWS_KEYS):
        values = []
        for key in keys:
            values.append(dictdata.get(key, None))
        return values
 
    """
    | news  | CREATE TABLE `news` (
  `id` char(64) DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `query` varchar(500) DEFAULT NULL,
  `channel` char(3) DEFAULT NULL,
  `type` char(3) DEFAULT NULL,
  `machineflag` char(12) DEFAULT NULL,
  `title` varchar(500) DEFAULT NULL,
  `body` longtext,
  `publishdate` char(19) DEFAULT NULL,
  `createdate` int(11) DEFAULT NULL,
  `updatedate` int(11) DEFAULT NULL,
  `cmtnum` bigint(15) DEFAULT NULL,
  `clicknum` bigint(15) DEFAULT NULL,
  `fansnum` bigint(15) DEFAULT NULL,
  `votenum` bigint(15) DEFAULT NULL,
  `key1` varchar(500) DEFAULT NULL,
  `key2` varchar(500) DEFAULT NULL,
  `key3` varchar(500) DEFAULT NULL,
  `key4` varchar(500) DEFAULT NULL,
  `key5` varchar(500) DEFAULT NULL,
  UNIQUE KEY `id` (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8 |
    """    
    """
    | comments | CREATE TABLE `comments` (
  `id` char(64) DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `content` longtext,
  `publishdate` char(19) DEFAULT NULL,
  `user` varchar(500) DEFAULT NULL,
  `createdate` int(11) DEFAULT NULL,
  `key1` varchar(500) DEFAULT NULL,
  `key2` varchar(500) DEFAULT NULL,
  `key3` varchar(500) DEFAULT NULL,
  `key4` varchar(500) DEFAULT NULL,
  `key5` varchar(500) DEFAULT NULL,
  UNIQUE KEY `id` (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8 |
    """
    """
    | querys | CREATE TABLE `querys` (
  `id` char(64) DEFAULT NULL,
  `query` varchar(500) DEFAULT NULL,
  `createdate` int(11) DEFAULT NULL,
  `updatedate` int(11) DEFAULT NULL,
  `machineflag` char(12) DEFAULT NULL,
  `key1` varchar(500) DEFAULT NULL,
  `key2` varchar(500) DEFAULT NULL,
  `key3` varchar(500) DEFAULT NULL,
  `key4` varchar(500) DEFAULT NULL,
  `key5` varchar(500) DEFAULT NULL,
  UNIQUE KEY `id` (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8 |
    """

if __name__ == '__main__':
    sql = SQLDAO()
    SQLDAO.getinstance().check()
    values = [['00001', 'http://www.sohu.com/', 'lol', '202', '302', int(time.time()),SpiderConfigure.getinstance().localmachineflag()],
              ['00002', 'http://www.sohu.com/', 'lol', '202', '302', int(time.time()),SpiderConfigure.getinstance().localmachineflag()]]  
    update = ['title', 'body', '2017-08-25 16:00:00', int(time.time()), '100', '100', '100', '100']
    update = dict(zip(SQLDAO.SPIDER_TABLE_NEWS_KEYS3, update))
    where = {SQLDAO.SPIDER_TABLE_NEWS_ID: '00001',SQLDAO.SPIDER_TABLE_NEWS_URL: 'http://www.sohu.com/'}
    if not SQLDAO.getinstance().exists(SQLDAO.SPIDER_TABLE_NEWS, where):
        SQLDAO.getinstance().insert(SQLDAO.SPIDER_TABLE_NEWS, SQLDAO.SPIDER_TABLE_NEWS_KEYS2, values, mutli=True)
    if SQLDAO.getinstance().exists(SQLDAO.SPIDER_TABLE_NEWS, where): 
        SQLDAO.getinstance().update(SQLDAO.SPIDER_TABLE_NEWS, where, update, relation='or')
    value = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: '00001'}, multi=False)
    wheref='{idkey}=\"{id}\"'
    where=wheref.format(idkey=SQLDAO.SPIDER_TABLE_NEWS_ID, id='00001')
    print SQLDAO.getinstance().count(SQLDAO.SPIDER_TABLE_NEWS, where=where)
    print value
    print dict(zip(SQLDAO.SPIDER_TABLE_NEWS_KEYS, value))
    print SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, where, [SQLDAO.SPIDER_TABLE_NEWS_ID], relation='or')
    print SQLDAO.getinstance().count(SQLDAO.SPIDER_TABLE_NEWS, where, relation='or')
    SQLDAO.getinstance().delete(SQLDAO.SPIDER_TABLE_NEWS, {SQLDAO.SPIDER_TABLE_NEWS_ID: '00002'})
    SQLDAO.getinstance().close()
    #print SQLDAO.getstring(sql.SPIDER_TABLE_QUERYS_KEYS)
    #print SQLDAO.getstring(sql.SPIDER_TABLE_NEWS_KEYS)
    #print SQLDAO.getstring(sql.SPIDER_TABLE_COMMENTS_KEYS)