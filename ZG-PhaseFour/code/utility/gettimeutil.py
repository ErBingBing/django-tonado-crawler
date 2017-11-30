# coding=utf-8

from utility.timeutility import TimeUtility
DEFAULTFORMAT = TimeUtility.DEFAULTFORMAT
#----------------------------------------------------------------------
def getuniformtime(string, format=DEFAULTFORMAT):
    return TimeUtility.getuniformtime(string, format)
#----------------------------------------------------------------------
def daycompare(t1, t2, days, format=DEFAULTFORMAT):
    return TimeUtility.daycompare(t1, t2, days, format)
#----------------------------------------------------------------------
def compareNow(curtime, days):
    """时间t比现在小多少天"""
    return TimeUtility.compareNow(curtime, days)
#----------------------------------------------------------------------
def isleap(year):
    return TimeUtility.isleap(year)
