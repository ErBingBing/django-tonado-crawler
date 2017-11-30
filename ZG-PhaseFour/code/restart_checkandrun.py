# encoding=utf-8
import os
import re
import shutil
import traceback
import time
from dateutil import parser
from datetime import datetime, timedelta
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
def restart(process='spider.py', cmd='sh /data/release/spider/startup.sh',secs=1):
    check = CHECK()
    print 'Checking process:'+process
    ids = check.getprocessid(process)
    while ids:
        if len(ids) >= 1:
            print process + ' already exsists! and now start to  kill '+process 
            check.killprocessid(ids)
        time.sleep(secs)
        ids = check.getprocessid(process)
    print 'Not exist process:'+process+', and restart process!'
    print 'EXECUTE CMD:\t'+cmd
    os.system(cmd)


def  clearfile(path='./logs', days=7, tmformat='%Y%m%d%H%M%S'):
    files = []
    if os.path.exists(path):
        files = os.listdir(path)
    for f in files:
        if re.search('\w+_(\d+)\.log', f):
            tms = re.findall('\w+_(\d+)\.log', f)[0]
            if  datetime.today() - datetime.strptime(f, tmformat) > timedelta(days):
                fpath = os.path.join(path, f)
                print 'Remove file:' + f
                os.remove(fpath)
'%Y%m%s%H%M%S'                

if __name__ == "__main__":
    #checkandrun(cmd='sh /mnt/data/release/spider/startup.sh', secs=60*5)
    #restart(process='checkandrun.py', cmd='sh checkandrun.sh') 
    clearfile()
