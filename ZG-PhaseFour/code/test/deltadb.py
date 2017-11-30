# -*- coding: utf-8 -*-
import os
import datetime
import sys


if __name__ == '__main__':
    workdir = os.path.dirname(os.path.abspath(__file__))
    while os.path.basename(workdir) != 'spider':
        workdir = os.path.dirname(workdir)
    sys.path.append(workdir)
    os.chdir(workdir)
    from dao.spiderdao import SpiderDao
    from storage.urlsstorage import URLCommentInfo
    from utility.gettimeutil import getuniformtime
    from utility.timeutility import TimeUtility
    db = SpiderDao()
    dict = db.getall()
    for key in dict.keys():
        value = dict[key]
        print db.getvalue(key)
        info = URLCommentInfo.fromstring(value)
        if info.clicknum > 10:
            info.clicknum -= 10
        else:
            info.clicknum = 0
        if info.cmtnum > 10:
            info.cmtnum -= 10
        else:
            info.cmtnum = 0
        if info.votenum > 10:
            info.votenum -= 10
        else:
            info.votenum = 0
        if info.fansnum > 10:
            info.fansnum -= 10
        else:
            info.fansnum = 0
        if info.realnum > 10:
            info.realnum -= 10
        else:
            info.realnum = 0
        if info.updatetime > TimeUtility.getuniformtime2(0):
            if len(info.updatetime) != 19:
                info.updatetime = getuniformtime(info.updatetime)
            dt = datetime.datetime.strptime(info.updatetime, TimeUtility.TIME_FORMAT_DEFAULT)
            info.updatetime = TimeUtility.getuniformtime(str(dt - datetime.timedelta(days=int(1))))

        print info.tostring()
        db.put(key, info.tostring())
    db.flush()
