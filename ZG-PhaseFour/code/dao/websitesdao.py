# -*- coding: utf-8 -*-

"""
# @file: cmtstorage.py
# @author: Sun Xinghua
# @date:  2017/6/7 16:09
# @version: Ver0.0.0.100
# @note:
"""
import json

from dao.mongodao import MongoDAO
from utility.regexutil import RegexUtility


class WebSiteDao:

    @staticmethod
    def loadfile(file):
        MongoDAO.getinstance().delete(MongoDAO.SPIDER_COLLECTION_WEBSITE, {}, False)
        jsonlist = []
        with open(file, 'r') as fp:
            for line in fp.readlines():
                jsonlist.append(json.loads(line.strip()))
            MongoDAO.insert(MongoDAO.SPIDER_COLLECTION_WEBSITE, jsonlist)
