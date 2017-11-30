# encoding=utf-8
import os
import re
import shutil
import traceback
import time
########################################################################
class CHECK:
    GREPCMD = "ps -ef|grep {process} > {tempfile}"
    KILLCMD = "kill {processid}"
    #----------------------------------------------------------------------
    def __init__(self):
        self.tempfile = '/data/temp.txt'

    def getprocessid(self, process, python=True):
        processid = []
        try:
            print 'EXECUTE CMD:\t'+self.GREPCMD.format(process=process, tempfile=self.tempfile)
            os.system(self.GREPCMD.format(process=process, tempfile=self.tempfile))
            if os.path.exists(self.tempfile):
                with open(self.tempfile) as fp:
                    for line in fp.readlines():
                        if line.strip():
                            print line.strip()
                            item = line.strip().split(' ')
                            item = [it.strip() for it in item if it.strip()]
                            if python:
                                if 'python'in line and item[-1] == process:
                                    #print line.strip()
                                    processid.append(item[1])
                            else:
                                if item[-1] == process:
                                    print line.strip()
                                    processid.append(item[1])
                os.remove(self.tempfile)
        except:
            traceback.print_exc()
        return processid

    def  killprocessid(self, processid):
        if isinstance(processid, str) or isinstance(processid, int):
            processid = list(processid)
        for item in processid:
            try:
                print "EXECUTE CMD:\t"+self.KILLCMD.format(processid=item)
                os.system(self.KILLCMD.format(processid=item))
            except:
                traceback.print_exc()

#----------------------------------------------------------------------
#循环执行某个python任务
def checkandrun(process='spider.py', cmd='sh ./startup.sh',secs=60):
    check = CHECK()
    print 'Checking process:'+process
    while True:
        ids = check.getprocessid(process)
        if len(ids) > 1:
            check.killprocessid(ids)
        elif len(ids) == 1:
            print process + ' already exsists!'
        else:
            print 'Not exist process:'+process+', and restart process!'
            print 'EXECUTE CMD:\t'+cmd
            os.system(cmd)
        print 'Sleeping {secs}s'.format(secs=secs)
        time.sleep(secs)
#----------------------------------------------------------------------
#kill某个python任务后再重启该任务
def killandrestart(process='autodownloader.py', cmd='sh ./autodownloader.sh', retrytimes=0):
    check = CHECK()
    print 'Checking process:'+process
    ids = check.getprocessid(process)
    if len(ids) >= 1:
        check.killprocessid(ids)
    print 'Not exist process:'+process+', and restart process!'
    print 'EXECUTE CMD:\t'+cmd
    os.system(cmd)
    time.sleep(60)
    if not check.getprocessid(process):
        print 'RESTART FAIL!'
        if retrytimes == 4:
            return 
        retrytimes += 1
        killandrestart(process, cmd, retrytimes)
    else:
        print 'RESTART SUCCESS!'
      
     
if __name__ == "__main__":
    killandrestart()
