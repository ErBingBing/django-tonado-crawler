## -*- coding: utf-8 -*-
####################################################################################################
## @file: fileformat.py
## @author: Sun Xinghua
## @date:  2016/12/15 13:26
## @version: Ver0.0.0.100
## @note:
####################################################################################################
##清洗数据
##1.notitle移除，输入到另外一个文件中
##2.nobody 移除且图片为空 ，输入到另外一个文件中
##3.pubtime不移除，但输入到另外一个文件中

#################################################################################################################
## @class：FileFormat
## @author：Sun Xinghua
## @date:  2016/12/15 13:26
## @note：主站工厂类
#################################################################################################################
#import math
#import os
#import sys
#import re
#import time
#import json
#import subprocess
#from configuration import constant
#from configuration.environment.configure import SpiderConfigure
##from dao.mongodao import MongoDAO
#from log.spiderlog import Logger
#from storage.cmtstorage import CMTStorage
#from storage.newsstorage import NewsStorage
#from storage.storage import Storage
#from utility import const
#from utility.common import Common
#from utility.fileutil import FileUtility
#from utility.timeutility import TimeUtility
#from log.spidernotify import SpiderNotify, NotifyParam
##from dao.channeldao import ChannelDao
#from configuration.constant import CHARSET_UTF8
#from utility.gettimeutil import getuniformtime
#class FileFormat:
    #FILE_MAX_LINES = 5000
    #PAGE_BASICINFO_LINES = 16

    #FILENAME_FORMAT1 = '{path}/{date}/{suffix}_{ts}_{channel}_{query}'
    #FILENAME_FORMAT2 = '{path}/{date}/{suffix}_{ts}_{channel}_{query}_SPLIT_{index}_{count}'
    #TIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    
    #if constant.DEBUG_FLAG == constant.DEBUG_FLAG_WINDOWS:
        #EXPORT_CMD = '{mongotools} -h {host} --port {port} -d {dbname} -c {collname} -q "{query}" -o {outputfile}'
    #else:
        #EXPORT_CMD = "{mongotools} -h {host} --port {port} -d {dbname} -c {collname} -q '{query}' -o {outputfile}"
    
    ##{'MD5':{"title":"",'cmtnum':}}
    #TITLE = MongoDAO.SPIDER_COLLECTION_NEWS_TITLE
    #CMTNUM = 'cmtnum'
    #NEWS_COMMENTS = {}
    #################################################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @note：初始化内部变量
    #################################################################################################################
    #def __init__(self):
        #self.inputpath = Storage.getstoragelocation(const.SPIDER_OUTPUT_TEMP_PATH)
        #self.outputpath = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                    #const.SPIDER_OUTPUT_PATH)
        #self.suffix = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,
                                                #const.SPIDER_OUTPUT_FILENAME_SUFFIX)
        #self.mongotools = SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN,
                                                #const.SPIDER_DATABASE_EXPORT_TOOLS)
        #self.ts = TimeUtility.getcurrentdate(TimeUtility.TIMESTAMP_FORMAT)
        #self.news_mongocollection = os.path.join(self.outputpath,TimeUtility.getcurrentdate()) + '/news_mongocollection_{t}.json'.format(t=self.ts)
        #self.cmts_mongocollection = os.path.join(self.outputpath,TimeUtility.getcurrentdate()) + '/cmts_mongocollection_{t}.json'.format(t=self.ts)
        #self.newsfile = self.getfilename(constant.SPIDER_CHANNEL_S3, MongoDAO.SPIDER_COLLECTION_NEWS, 0)
        #self.newsfile_top = self.getfilename(constant.SPIDER_CHANNEL_S3, MongoDAO.SPIDER_COLLECTION_NEWS+'_top', 0)
        #self.cmtsfile = self.getfilename(constant.SPIDER_CHANNEL_S3, MongoDAO.SPIDER_COLLECTION_COMMENTS, 0)
        #self.news_errorfile =  os.path.join(self.outputpath,TimeUtility.getcurrentdate()) + '/news_errorfile_{t}'.format(t=self.ts)       
        #self.retrytimes = int(SpiderConfigure.getconfig(const.SPIDER_EXCEPTION_DOMAIN, const.SPIDER_UPLOAD_RETRY_TIMES))
    #################################################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @note：初始化内部变量
    #################################################################################################################
    ##def format(self):
        ##Logger.getlogging().debug(SpiderConfigure.getinstance().starttime())
        ##newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {'$gte': SpiderConfigure.getinstance().starttime()}}
        ##NewsStorage.writetofile(self.newsfile,cond=newscond)       
        ##comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {'$gte': SpiderConfigure.getinstance().starttime()}}
        ##CMTStorage.writetofile(self.cmtsfile,cond=comments_cond)
    #def format(self, starttime=0, endtime=0, top=False):
        ##1.mongoexport 导出过滤条件的文件
        ##2.转换格式为输出文件的格式
        #if starttime:
            #starttime = int(starttime)
        #if endtime:
            #endtime = int(endtime)
        #if top:
            #if starttime and endtime:
                #Logger.getlogging().debug(endtime)
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": starttime, "$lte":endtime},
                          #MongoDAO.SPIDER_COLLECTION_NEWS_TOP_FLAG:top}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": starttime, "$lte":endtime}}
            #elif starttime:
                #Logger.getlogging().debug(starttime)
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": starttime},
                          #MongoDAO.SPIDER_COLLECTION_NEWS_TOP_FLAG:top}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": starttime}}
            #else:
                #Logger.getlogging().debug(SpiderConfigure.getinstance().starttime())
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": SpiderConfigure.getinstance().starttime()},
                          #MongoDAO.SPIDER_COLLECTION_NEWS_TOP_FLAG:top}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": SpiderConfigure.getinstance().starttime()}}            
        #else:
            #if starttime and endtime:
                #Logger.getlogging().debug(endtime)
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": starttime, "$lte":endtime}}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": starttime, "$lte":endtime}}
            #elif starttime:
                #Logger.getlogging().debug(starttime)
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": starttime}}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": starttime}}
            #else:
                #Logger.getlogging().debug(SpiderConfigure.getinstance().starttime())
                #newscond={MongoDAO.SPIDER_COLLECTION_NEWS_UPDATE_DATE: {"$gte": SpiderConfigure.getinstance().starttime()}}
                #comments_cond = {MongoDAO.SPIDER_COLLECTION_COMMENTS_CREATE_DATE: {"$gte": SpiderConfigure.getinstance().starttime()}}
        
        ##导出新闻
        #if self.mongoexport(MongoDAO.SPIDER_COLLECTION_NEWS, json.dumps(newscond), self.news_mongocollection):
            #Logger.getlogging().debug('Now, Starting Output News Infomation To {f}'.format(f=self.newsfile))
            #Logger.getlogging().debug('Now, Starting Output Error News Infomation To {f}'.format(f=self.news_errorfile))            
            #self.newsjson2file(self.news_mongocollection, self.newsfile_top, self.newsfile, self.news_errorfile)  
        #Logger.getlogging().debug('News Finish')
        ##更新错误的新闻标记
        #Logger.getlogging().debug('Now, Starting Renew  Error News Infomation To {f}'.format(f=self.news_errorfile))                    
        #FileFormat.renewerrornews(self.news_errorfile)
        ##导出评论
        #if self.mongoexport(MongoDAO.SPIDER_COLLECTION_COMMENTS, json.dumps(comments_cond), self.cmts_mongocollection):
            #Logger.getlogging().debug('Now, Starting Output CMTS Infomation To {f}'.format(f=self.cmtsfile))  
            #self.commetsjson2file(self.cmts_mongocollection, self.cmtsfile)
        #Logger.getlogging().debug('Comments Finish')
        
    #def mongoexport(self, collname, query, outputfile):
        #Logger.getlogging().debug('From Collection {c} Export Data To File {f}'.format(c=collname, f=outputfile))
        ##mongoexport -d spider -c News -q '{"id":"2ccb989d1ac2a0b301da74ff83f6531a"}' -o newstest.json
        #cmd = self.EXPORT_CMD.format(mongotools=self.mongotools, 
                                     #host=SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_IP),
                                     #port=SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_PORT),
                                     #dbname=SpiderConfigure.getconfig(const.SPIDER_DATABASE_DOMAIN, const.SPIDER_DATABASE_DATABASE), 
                                     #collname=collname,
                                     #query=query,
                                     #outputfile=outputfile)
        #Logger.getlogging().debug(cmd)
        #if self.execute(cmd):
            #time.sleep(2)
            #if FileUtility.exists(outputfile):
                #return True
        #secs = 10
        #for count in range(0, self.retrytimes):
            #time.sleep(secs)
            #secs *= 2
            #if self.execute(cmd):
                #time.sleep(2)
                #if FileUtility.exists(outputfile):
                    #return True
        #else:
            #param = NotifyParam()
            #param.code = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED
            #param.message = NotifyParam.SPIDER_NOTIFY_UPLOAD_FAILED_MESSAGE_FORMAT.format(
                #file=FileUtility.getfilename(outputfile), taskid=self.mongotools)
            #SpiderNotify.notify(param)
            #return False
    
    #@staticmethod
    #def newsjson2file(jsonfile, outputfile_top, outputfile, news_errorfile):
        #lines = []
        #with open(jsonfile, 'r') as fp:
            #lines = fp.readlines()
        #for line in lines:
            #try:
                #doc = json.loads(line)
                #url = FileFormat.filterstr(doc[MongoDAO.SPIDER_COLLECTION_NEWS_URL])
                #media = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_MEDIA_NAME in doc:
                    #media = doc[MongoDAO.SPIDER_COLLECTION_NEWS_MEDIA_NAME]
                #image = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_IMAGE_URL in doc:
                    #image = doc[MongoDAO.SPIDER_COLLECTION_NEWS_IMAGE_URL]
                    #if  isinstance(image,list):
                        #imageurl = '|'.join(image)
                        #imglist = []
                        #for img in image:
                            #try:
                                #imgcon = NewsStorage.getimage(img).strip()
                            #except:
                                #Logger.printexception()
                                #imgcon = ''
                            #if imgcon:
                                #imglist.append(imgcon)
                        #image = '|'.join(imglist)
                        #if not image:
                            #image = 'no image'
                    #else:
                        #imageurl = image
                        #image = image
                #title = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_TITLE in doc:
                    #title = doc[MongoDAO.SPIDER_COLLECTION_NEWS_TITLE]
                #content = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_BODY in doc:
                    #content = doc[MongoDAO.SPIDER_COLLECTION_NEWS_BODY]
                #publishdate = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_PUBLISH_DATE in doc:
                    #publishdate = doc[MongoDAO.SPIDER_COLLECTION_NEWS_PUBLISH_DATE]
                    #if publishdate:
                        #try:
                            #publishdate = int(time.mktime(time.strptime(publishdate,'%Y-%m-%d %H:%M:%S')))
                        #except:
                            #Logger.printexception()
                            #publishdate = 0
                #top = ''
                #if MongoDAO.SPIDER_COLLECTION_NEWS_TOP_FLAG in doc:
                    #top = doc[MongoDAO.SPIDER_COLLECTION_NEWS_TOP_FLAG]
                    #if top:
                        #top = 'true'
                ##清洗数据
                ##1.notitle移除，输入到另外一个文件中
                ##2.nobody 移除且图片为空 ，输入到另外一个文件中
                ##3.media pubtime不移除，但输入到另外一个文件中 
                #errorfstring = NewsStorage.NEWS_OTHERFORMAT.format(channel=ChannelDao.getchannel(url),
                                                                 #url=url,
                                                                 #title=FileFormat.filterstr(title),
                                                                 #content=FileFormat.filterstr(content),
                                                                 #publishdate=publishdate,
                                                                 #media=media,
                                                                 #image=imageurl,
                                                                 #top=top)
                #if title == 'no title' or not title:
                    #FileUtility.writeline(news_errorfile, errorfstring.encode(CHARSET_UTF8))
                    #continue
                #if (content == 'no body' or not content) and (imageurl == 'no image' or not imageurl):
                    #FileUtility.writeline(news_errorfile, errorfstring.encode(CHARSET_UTF8))
                    #continue
                #if '504 Gateway Time-out' in content or u'404-找不到文件或目录' in content or u'服务器错误' in title:
                    #FileUtility.writeline(news_errorfile, errorfstring.encode(CHARSET_UTF8))
                    #continue
                #if media == 'no name' or not media:
                    #FileUtility.writeline(news_errorfile, errorfstring.encode(CHARSET_UTF8))
                #if publishdate == '1970-01-01 08:00:00' or not publishdate:
                    #FileUtility.writeline(news_errorfile, errorfstring.encode(CHARSET_UTF8))
    
                #fstring = NewsStorage.NEWS_FORMAT.format(channel=ChannelDao.getchannel(url),
                                                         #url=url,
                                                         #ourl=url,
                                                         #title=FileFormat.filterstr(title),
                                                         #content=FileFormat.filterstr(content),
                                                         #publishdate=publishdate,
                                                         #media=media,
                                                         #image=image,
                                                         #top=top)
                #if top:
                    #FileUtility.writeline(outputfile_top, fstring.encode(CHARSET_UTF8)) 
                #else:
                    #FileUtility.writeline(outputfile, fstring.encode(CHARSET_UTF8))
            #except:
                #Logger.printexception()
        #FileUtility.flush()    
        
    #@staticmethod
    #def commetsjson2file(jsonfile, outputfile):
        #lines = []
        #with open(jsonfile, 'r') as fp:
            #lines = fp.readlines()
        #for line in lines:
            #try:
                #doc = json.loads(line)
                #url = FileFormat.filterstr(doc[MongoDAO.SPIDER_COLLECTION_COMMENTS_URL])
                #key = Common.md5(url)
                #if key in FileFormat.NEWS_COMMENTS:
                    #title = FileFormat.NEWS_COMMENTS[key][FileFormat.TITLE]
                    #cmtnum = FileFormat.NEWS_COMMENTS[key][FileFormat.CMTNUM]
                #else:
                    #FileFormat.NEWS_COMMENTS[key] = {}
                    #FileFormat.NEWS_COMMENTS[key][FileFormat.TITLE] = NewsStorage.gettitle(url)
                    #FileFormat.NEWS_COMMENTS[key][FileFormat.CMTNUM] = CMTStorage.getcount(url)
                #fstring = CMTStorage.COMMENTS_FORMAT.format(channel=ChannelDao.getchannel(url),
                                                            #content=FileFormat.filterstr(doc[MongoDAO.SPIDER_COLLECTION_COMMENTS_CONTENT]),
                                                            #cmtnum=FileFormat.NEWS_COMMENTS[key][FileFormat.CMTNUM],
                                                            #publishdate=doc[MongoDAO.SPIDER_COLLECTION_COMMENTS_PUBLISH_DATE],
                                                            #user=doc[MongoDAO.SPIDER_COLLECTION_COMMENTS_USER],
                                                            #url=url,
                                                            #title=FileFormat.filterstr(FileFormat.NEWS_COMMENTS[key][FileFormat.TITLE]))
                #FileUtility.writeline(outputfile, fstring.encode(CHARSET_UTF8))   
            #except:
                #Logger.printexception()
        #FileUtility.flush()
    
    #@staticmethod
    #def renewerrornews(errorfile):
        #lines = []
        #if FileUtility.exists(errorfile):
            #with open(errorfile, 'r') as fp:
                #lines = fp.readlines()
        ##对错误的进行标记，以便下一次运行时重新更新
        ##此时的格式为NewsStorage.NEWS_OTHERFORMAT
        #for line in lines:
            #try:
                #url = line.split('\t')[1].strip()
                #if NewsStorage.exist(url):
                    #id = NewsStorage.getid(url)
                    #Logger.getlogging().debug(url)
                    #MongoDAO.getinstance().update(MongoDAO.SPIDER_COLLECTION_NEWS, 
                                                  #{MongoDAO.SPIDER_COLLECTION_NEWS_INDEX: id},
                                                  #{MongoDAO.SPIDER_COLLECTION_NEWS_RENEW: True})
            #except:
                #Logger.printexception()
                
    #def formatfolder(self, path):
        #files = FileUtility.getfilelist(path, [])
        #pageindex = 0
        #pagecount = int(math.ceil(float(len(files)) / FileFormat.FILE_MAX_LINES))
        #linecount = 0
        #filename = None
        #for fl in files:
            #(lines, channel, query) = self.readfile(fl)
            #for line in lines:
                #if linecount % self.FILE_MAX_LINES == 0:
                    #pageindex += 1
                    #filename = self.getfilename(channel, query, pageindex, pagecount)
                    #Logger.getlogging().info(filename)
                    #if FileUtility.exists(filename):
                        #FileUtility.remove(filename)
                #FileUtility.writeline(filename, line)
                #linecount += 1
        #FileUtility.flush()

    #################################################################################################################
    ## @functions：__init__
    ## @param： none
    ## @return：none
    ## @note：初始化内部变量
    #################################################################################################################
    #def getfilename(self, channel, query, index, total=1):
        #ts = time.strftime('%Y%m%d%H',time.localtime(time.time()-60*60))
        #if total == 1:
            #return self.FILENAME_FORMAT1.format(path=self.outputpath, date=TimeUtility.getcurrentdate(),
                                                #suffix=self.suffix, ts=ts,
                                                #channel=channel, query=query)
        #else:
            #return self.FILENAME_FORMAT2.format(path=self.outputpath, date=TimeUtility.getcurrentdate(),
                                                #suffix=self.suffix, ts=ts,
                                                #channel=channel, query=query, index=index, count=total)

    #def execute(self, cmd):
        #Logger.getlogging().info('Execute command:{cmd}'.format(cmd=cmd))
        #subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #subp.wait()
        #c = subp.stdout.readline()
        #while c:
            #if subp.returncode != 0:
                #Logger.getlogging().error(c.strip())
            #else:
                #Logger.getlogging().info(c.strip())
            #c = subp.stdout.readline()
        #e = subp.stderr.readline()
        #while e:
            #if subp.returncode != 0:
                #Logger.getlogging().error(e.strip())
            #else:
                #Logger.getlogging().info(e.strip())
            #e = subp.stderr.readline()
        #if subp.returncode != 0:
            #Logger.getlogging().error('Execute command:{cmd} failed'.format(cmd=cmd))
            #return False
        #return True
    #@staticmethod
    #def filterstr(string):
        #special = [' ','\n', '\r', '\t']
        #for s in special:
            #string = string.replace(s, '')
        #return string
#if __name__ == '__main__':
    ##参数:-starttime,--starttime表示开始时间，可以是时间戳或者'2017-08-01 00:00:00'时间格式
    ##     -endtime,--endtime    表示结束时间，可以是时间戳或者'2017-08-01 00:00:00'时间格式
    ##     -top,--top            表示是否只输出头条，可以是True,true或者False,false
    ##例:  python fileformat.py -starttime "2017-08-01 00:00:00" -top=True
    #argk = ['-starttime','--starttime','-endtime','--endtime','-top','--top']
    #argv = sys.argv
    ##argv = ['python', 'fileformat.py', '-starttime','2017-08-01 00:00:00', '-endtime=2017-08-01 00:00:00','-top=True',]
    #args = {}
    #if len(argv) >= 2:
        #for pos in range(len(argv)):
            #v = None
            #k = argv[pos].split('=')[0]
            #if k in argk:
                #if k+'=' in argv[pos]:
                    #v = argv[pos].split('=')[-1]
                #elif k in argv[pos] and pos+1 < len(argv):
                    #v = argv[pos+1]
            #if k and v:
                #if k.startswith('--'):
                    #k=k.split('--')[-1]
                #elif k.startswith('-'):
                    #k=k.split('-')[-1]                 
                #if  str(v).lower() == "true":
                    #v = True
                #elif  str(v).lower() == "false":
                    #v = False                 
                #if re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(v)):
                    #v = int(time.mktime(time.strptime(v, '%Y-%m-%d %H:%M:%S')))            
                #args[k] = v
        #FileFormat().format(**args)
    #else:
        #FileFormat().format(0)     
        
        
    ##if len(argv) >= 2:
        ##for arg in argk:
            ##k = None
            ##v = None
            ##if arg.startswith('--'):
                ##k=arg.split('--')[-1]
            ##else:
                ##k=arg.split('-')[-1]            
            ##if arg in argv:
                ##pos = argv.index(arg)
                ##v = argv[pos+1]
            ##for pos in range(len(argv)):
                ##if re.search(arg+"=",argv[pos]):
                    ##v = argv[pos].split('=')[-1]
                    ##break
            ##if k and v:
                ##if  str(v).lower() == "true":
                    ##v = True
                ##elif  str(v).lower() == "false":
                    ##v = False                 
                ##if re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(v)):
                    ##v = int(time.mktime(time.strptime(v, '%Y-%m-%d %H:%M:%S')))
                ##args[k] = v
        ##FileFormat().format(**args)
    ##else:
        ##FileFormat().format(0)        
                
    ##if len(sys.argv) == 4:
        ##if re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',str(sys.argv[1])) and re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',str(sys.argv[2])):
            ##start = time.mktime(time.strptime(str(sys.argv[1]),'%Y-%m-%d %H:%M:%S'))
            ##end = time.mktime(time.strptime(str(sys.argv[2]),'%Y-%m-%d %H:%M:%S'))
            ##top = str(sys.argv[3])
            ##FileFormat().format(int(start), int(end), top)
        ##elif re.search('\d{10}',str(sys.argv[1])) and re.search('\d{10}',str(sys.argv[2])):
            ##start = sys.argv[1]
            ##end = sys.argv[2]
            ##FileFormat().format(int(start), int(end))
        ##else:
            ##print 'ERROR FORMAT'             
    ##elif len(sys.argv) == 3:
        ##if re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',str(sys.argv[1])) and re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',str(sys.argv[2])):
            ##start = time.mktime(time.strptime(str(sys.argv[1]),'%Y-%m-%d %H:%M:%S'))
            ##end = time.mktime(time.strptime(str(sys.argv[2]),'%Y-%m-%d %H:%M:%S'))
            ##FileFormat().format(int(start), int(end))
        ##elif re.search('\d{10}',str(sys.argv[1])) and re.search('\d{10}',str(sys.argv[2])):
            ##start = sys.argv[1]
            ##end = sys.argv[2]
            ##FileFormat().format(int(start), int(end))
        ##else:
            ##print 'ERROR FORMAT'        
    ##elif len(sys.argv) == 2:
        ##if re.search('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',str(sys.argv[1])):
            ##t = time.mktime(time.strptime(str(sys.argv[1]),'%Y-%m-%d %H:%M:%S'))
            ##FileFormat().format(int(t))
        ##elif re.search('\d{10}',str(sys.argv[1])):
            ##t= sys.argv[1]
            ##FileFormat().format(int(t))
        ##else:
            ##print 'ERROR FORMAT'
    ##else:
        ##t = '2017-07-24 00:00:00'
        ##t = time.mktime(time.strptime(t,'%Y-%m-%d %H:%M:%S'))
        ##FileFormat().format(int(t))
            
        
