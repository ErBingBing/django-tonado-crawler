# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################
import bsddb
from configuration.constant import const
from configuration.environment.configure import SpiderConfigure
from utility.fileutil import FileUtility


################################################################################################################
# @class：SpiderDao
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class SpiderDao:
    cachedict = {}

    ##############################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SpiderDao类的构造器，初始化内部变量
    ##############################################################################################
    def __init__(self):
        self.dbfile = SpiderConfigure.getconfig(const.SPIDER_DB_DOMAIN, const.SPIDER_DB_FILEPATH)

    ##############################################################################################
    # @functions：getvalue
    # @param：key
    # @return：value or None
    # @note：先从内存中查找，如果没有从DB中获取
    ##############################################################################################
    def getvalue(self, key):
        value = None
        if key in SpiderDao.cachedict:
            value = SpiderDao.cachedict[key]
        elif FileUtility.exists(self.dbfile):
            database = bsddb.btopen(self.dbfile, 'r')
            if database.has_key(key):
                value = database[key]
                SpiderDao.cachedict[key] = value
            database.close()
        return value

    ####################################################################################
    # @functions：put
    # @param：key
    # @param：value
    # @return：none
    # @note：存储数据到DB
    ##############################################################################################
    def put(self, key, value):
        if key in SpiderDao.cachedict:
            SpiderDao.cachedict[key] = value
        database = bsddb.btopen(self.dbfile, 'c')
        database[key] = value
        database.close()

    ####################################################################################
    # @functions：flush
    # @param：key
    # @param：value
    # @return：none
    # @note：存储数据到DB
    ##############################################################################################
    def flush(self):
        database = bsddb.btopen(self.dbfile, 'c')
        for key in SpiderDao.cachedict.keys():
            database[key] = SpiderDao.cachedict[key]
        database.close()

    ####################################################################################
    # @functions：getall
    # @param：none
    # @return：数据库中所有的数据
    # @note：从数据库中获取所有的数据
    ##############################################################################################
    def getall(self):
        resdict = None
        if FileUtility.exists(self.dbfile):
            database = bsddb.btopen(self.dbfile, 'r')
            resdict = {}
            for key in database.keys():
                resdict[key] = database[key]
            database.close()
        return resdict

    ####################################################################################
    # @functions：remove
    # @param：keys
    # @return：none
    # @note：从数据库中删除数据
    ##############################################################################################
    def remove(self, keys):
        if FileUtility.exists(self.dbfile):
            database = bsddb.btopen(self.dbfile, 'w')
            for key in keys:
                database.__delitem__(key)
            database.close()
