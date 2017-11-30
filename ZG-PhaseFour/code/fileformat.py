# encoding=utf-8
import os
import time
from  utility.timeutility import TimeUtility
from  utility.fileutil import FileUtility 
from storage.newsstorage import NewsStorage
from storage.cmtstorage  import CMTStorage
from dao.sqldao import SQLDAO  
from utility.common  import Common
from utility import const
from configuration import constant
from configuration.environment.configure import SpiderConfigure
from log.spiderlog import Logger
########################################################################
class FileFormat:
    """"""
    DEFAULT_NEWS_FORMAT = u'{channel}\t{url}\t{title}\t{body}\t{comments}\t{cmtnum}\t{clicknum}\t{votenum}\t{fansnum}\t{pubtime}\t{crawlertime}\t{type}\t{query}\t\t\t'
    KEY_CMTLIST = 'commentlist'
    OUTPUTPATH = '{path}/{suffix}_{date}_{ts}'
    ERRORINFOPATH = '{path}/{suffix}_error_{date}_{ts}'
    #----------------------------------------------------------------------
    def __init__(self):
        self.url_beforenewsinfo_map = {SQLDAO.SPIDER_TABLE_NEWS_CMTNUM: {},
                                       SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM: {},
                                       SQLDAO.SPIDER_TABLE_NEWS_VOTENUM: {},
                                       SQLDAO.SPIDER_TABLE_NEWS_FANSNUM: {}}
        self.url_beforenewsnum_map = {}
        self.url_curcmtcontent_map = {}
        self.url_curcmtnum_map = {}
        self.url_beforecmtnum_map = {}
        date = TimeUtility.getcurrentdate()
        path = os.path.join(SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_OUTPUT_PATH), date)     
        suffix = SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_OUTPUT_FILENAME_SUFFIX)  
        self.outputpath = FileFormat.OUTPUTPATH.format(path=path, suffix=suffix, date=date.replace('-', '_'), ts=int(time.time()))
        self.errorinfopath = FileFormat.ERRORINFOPATH.format(path=path, suffix=suffix, date=date.replace('-', '_'), ts=int(time.time()))
        self.pushpath = os.path.join(SpiderConfigure.getconfig(const.SPIDER_STORAGE_DOMAIN,const.SPIDER_PUSH_PATH_MASTER), date)
        if not FileUtility.exists(path):
            FileUtility.mkdirs(path)    
        #if not FileUtility.exists(self.pushpath):
            #FileUtility.mkdirs(self.pushpath)

    #----------------------------------------------------------------------
    def dereplicate(self):
        #聚合相关信息后, 执行去重
        #获取本次所有key1=null且channel=201的所有url为urllist
        #遍历urllist中的url，且key1=null,channel=202的所有id为idlist
        #对idlist中的kye1打标记，该条记录不在输出
        idlist = []
        sql = 'SELECT url from news where key1 is null and channel=201'
        sqlf= 'SELECT id  from news where url=\"{url}\" and key1 is null and channel=202'
        results = SQLDAO.getinstance().execute(sql, find=True)    
        for result in results:
            sql2 = sqlf.format(url=result[0])
            results2 = SQLDAO.getinstance().execute(sql2, find=True) 
            if results2:
                Logger.getlogging().info('dereplicated url:\t{url}'.format(url=result[0]))
            for result2 in results2:
                idlist.append(result2[0])
        self.updatenewsflag(idlist)
        
    #----------------------------------------------------------------------
    def fileformat(self):
        self.aggregate_beforenewsinfo()
        self.aggregate_beforenewsnum()        
        self.aggregate_curcomments()
        self.aggregate_curcmtnum()
        self.aggregate_beforecmtsnum()
        self.dereplicate()
        urllist = []
        idlist = []
        newscond = '{key} is null'.format(key=SQLDAO.SPIDER_TABLE_NEWS_KEY1)
        results = SQLDAO.getinstance().find(SQLDAO.SPIDER_TABLE_NEWS, where=newscond)
        for result in results:
            doc = SQLDAO.getdictdata(SQLDAO.SPIDER_TABLE_NEWS_KEYS, result)
            id = doc[SQLDAO.SPIDER_TABLE_NEWS_ID]
            url = doc[SQLDAO.SPIDER_TABLE_NEWS_URL].strip()            
            try:
                urlmd5 = Common.md5(url)
                channel = doc.get(SQLDAO.SPIDER_TABLE_NEWS_CHANNEL, '201')
                title = doc.get(SQLDAO.SPIDER_TABLE_NEWS_TITLE, '')
                body = doc.get(SQLDAO.SPIDER_TABLE_NEWS_BODY, '')
                commentlist = self.url_curcmtcontent_map.get(urlmd5, [])
                comments = ' '.join(commentlist)
                pubtime = doc.get(SQLDAO.SPIDER_TABLE_NEWS_PUBLISH_DATE, TimeUtility.getintformtime(0))
                crawlertime = doc.get(SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE, TimeUtility.getintformtime(0))
                type = doc.get(SQLDAO.SPIDER_TABLE_NEWS_TYPE, '')
                query = doc.get(SQLDAO.SPIDER_TABLE_NEWS_QUERY, '')
                #评论量增量推送
                #      第一次推送全量：如果comments对应的内容没有被取过(key1没有标记1)，则应推送全量
                #                     此时如果news中cmtnum>0,则推送news中的cmtnum，否则推送comment中的cmtnum(已经聚合到url_curcmtnum_map中)                             
                #      第二次推送增量：如果comments对应的内容有取过(key1有部分标记1)，则应推送增量，推送comment中的cmtnum(已经聚合到url_curcmtnum_map中)
                cmtkey1flag = self.url_beforecmtnum_map.get(urlmd5, -1)
                if cmtkey1flag <= 0:
                    cmtnum = doc.get(SQLDAO.SPIDER_TABLE_NEWS_CMTNUM, -1)
                    if cmtnum < 0:
                        cmtnum = self.url_curcmtnum_map.get(urlmd5, 0)
                else:
                    cmtnum = self.url_curcmtnum_map.get(urlmd5, 0)
                #其他增量
                clicknum = doc.get(SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM, -1)
                clicknum = self.increment(urlmd5, SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM, clicknum)
                votenum = doc.get(SQLDAO.SPIDER_TABLE_NEWS_VOTENUM, -1)
                votenum = self.increment(urlmd5, SQLDAO.SPIDER_TABLE_NEWS_VOTENUM, votenum)
                fansnum = doc.get(SQLDAO.SPIDER_TABLE_NEWS_FANSNUM, -1)
                fansnum = self.increment(urlmd5, SQLDAO.SPIDER_TABLE_NEWS_FANSNUM, fansnum)
                string = FileFormat.DEFAULT_NEWS_FORMAT.format(channel=channel,
                                                               url=url,
                                                               title=self.strfilter(title),
                                                               body=self.strfilter(body),
                                                               comments=comments,
                                                               cmtnum=cmtnum,
                                                               clicknum=clicknum,
                                                               votenum=votenum,
                                                               fansnum=fansnum,
                                                               pubtime=TimeUtility.getinttime(pubtime),
                                                               crawlertime=crawlertime,
                                                               type=type,
                                                               query=self.strfilter(query))   
                Logger.getlogging().info(u'{channel}\t{query}\t{url}'.format(channel=channel, query=query, url=url).encode(constant.CHARSET_UTF8))
                if not title:
                    FileUtility.writeline(self.errorinfopath, string.encode(constant.CHARSET_UTF8)) 
                else:
                    FileUtility.writeline(self.outputpath, string.encode(constant.CHARSET_UTF8))  
          
                if id not in idlist:
                    idlist.append(id)
                if title and commentlist:
                    if url not in urllist:
                        urllist.append(url)
            except:
                Logger.getlogging().error(str(result))
                Logger.printexception()
        #已经提取过，则变更key1标记为1
        self.updatenewsflag(idlist)
        self.updatecommentsflag(urllist)
        ##推送数据到指定路径
        #if FileUtility.exists(self.outputpath):
            #FileUtility.copy(self.outputpath, self.pushpath)
    #----------------------------------------------------------------------
    def increment(self, urlmd5, key, curnum):
        #计算增量
        #1.当前某字段取值<=0,则表示该字段未取到值或者等于0,此时无法计算增量（不需要计算增量）
        #2.当前某字段取值>0, 则表示该字段正常取值，此时可以计算增量
        #      2.1如果该url是新url(key1没有标记1)，返回该值
        #      2.2如果该url是旧url(key1有部分标记1),则用当前量减去已经取过的量的最大值【因为增量始终是最大值之差】
        #      2.3在2.2情况下如何提取已取过url的最大值，首先是值是有效的，其次是按抓取时间排序，取最大抓取时间对应的值          
        if curnum <= 0:
            return 0   
        newskey1flag = self.url_beforenewsnum_map.get(urlmd5, -1)
        if newskey1flag > 0:
            before = self.url_beforenewsinfo_map[key].get(urlmd5, 0)
            curnum = curnum - before
        return curnum   
    #----------------------------------------------------------------------
    def aggregate_curcomments(self):
        #汇总本次未推送的评论
        sqlf = 'SELECT {url},{content},{publish} from {table} where {key1} is null'
        sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_COMMENTS,
                          url=SQLDAO.SPIDER_TABLE_COMMENTS_URL,
                          content=SQLDAO.SPIDER_TABLE_COMMENTS_CONTENT,
                          publish=SQLDAO.SPIDER_TABLE_COMMENTS_PUBLISH_DATE,
                          key1=SQLDAO.SPIDER_TABLE_COMMENTS_KEY1)
        cmtsresults = SQLDAO.getinstance().execute(sql, find=True)
        for cmtsresult in cmtsresults:
            urlmd5 = Common.md5(cmtsresult[0])
            content = self.strfilter(cmtsresult[1])
            publish = TimeUtility.getinttime(cmtsresult[2])
            if urlmd5 not in self.url_curcmtcontent_map:
                self.url_curcmtcontent_map[urlmd5] = []
            self.url_curcmtcontent_map[urlmd5].append(content + '_' + str(int(publish)))
        
    #----------------------------------------------------------------------
    def aggregate_curcmtnum(self):
        #计算本次未推送过的评论数量
        sqlf = 'SELECT {url},count(*) from {table} where {key1} is null group by {url}'
        sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_COMMENTS,
                          url=SQLDAO.SPIDER_TABLE_COMMENTS_URL,
                          key1=SQLDAO.SPIDER_TABLE_COMMENTS_KEY1)
        results = SQLDAO.getinstance().execute(sql, find=True)
        for result in results:
            key = Common.md5(result[0].strip())
            if key not in self.url_curcmtnum_map:
                self.url_curcmtnum_map[key] = int(result[1])
    #----------------------------------------------------------------------
    def aggregate_beforecmtsnum(self):
        #计算本次之前已经推送过的数量
        #如果key1标记为1,则表示该url对应的comments已经推送过一部分；否则表示未推送过
        sqlf = 'SELECT {url},count(*) from {table} where {key1}=1 group by {url}'
        sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_COMMENTS,
                          url=SQLDAO.SPIDER_TABLE_COMMENTS_URL,
                          key1=SQLDAO.SPIDER_TABLE_COMMENTS_KEY1)   
        results = SQLDAO.getinstance().execute(sql, find=True)
        for result in results:
            key = Common.md5(result[0].strip())
            if key not in self.url_beforecmtnum_map:
                self.url_beforecmtnum_map[key] = int(result[1])        
                
    #----------------------------------------------------------------------
    def aggregate_beforenewsinfo(self):
        #如何提取已取过url的最大值
        #1.首先值是有效的，并存储对应的值的抓取时间
        #2.其次按抓取时间排序，取最大抓取时间对应的值
        sqlf = 'SELECT {url},{createtime},{cmtnum}, {clicknum},{votenum},{fansnum} from {table} where  {key1}=1'
        sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_NEWS,
                          url=SQLDAO.SPIDER_TABLE_NEWS_URL,
                          createtime=SQLDAO.SPIDER_TABLE_NEWS_CREATE_DATE,
                          cmtnum=SQLDAO.SPIDER_TABLE_NEWS_CMTNUM,
                          clicknum=SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM,
                          votenum=SQLDAO.SPIDER_TABLE_NEWS_VOTENUM,
                          fansnum=SQLDAO.SPIDER_TABLE_NEWS_FANSNUM,
                          key1=SQLDAO.SPIDER_TABLE_NEWS_KEY1)
        results = SQLDAO.getinstance().execute(sql, find=True)
        cmtnumlist = {}
        clicknumlist = {}
        votenumlist = {}
        fansnumlist = {}
        for result in results:
            url = result[0].strip()
            urlmd5 = Common.md5(url)
            createtime = result[1]
            cmtnum = result[2]
            clicknum = result[3]
            votenum = result[4]
            fansnum = result[5]
            if urlmd5 not in cmtnumlist:
                cmtnumlist[urlmd5] = {}
            if urlmd5 not in clicknumlist:
                clicknumlist[urlmd5] = {}
            if urlmd5 not in votenumlist:
                votenumlist[urlmd5] = {}
            if urlmd5 not in fansnumlist:
                fansnumlist[urlmd5] = {}
            #存储有效的值(>0)及对应的抓取时间
            if cmtnum > 0:
                if cmtnumlist[urlmd5].get(str(createtime), 0) <= cmtnum:
                    cmtnumlist[urlmd5][str(createtime)] = cmtnum
            if clicknum > 0:
                if clicknumlist[urlmd5].get(str(createtime), 0) <= clicknum:
                    clicknumlist[urlmd5][str(createtime)] = clicknum
            if votenum > 0:
                if votenumlist[urlmd5].get(str(createtime), 0) <= votenum:
                    votenumlist[urlmd5][str(createtime)] = votenum            
            if fansnum > 0:
                if fansnumlist[urlmd5].get(str(createtime), 0) <= fansnum:
                    fansnumlist[urlmd5][str(createtime)] = fansnum 
        for urlmd5, value in cmtnumlist.iteritems():
            if not value:
                continue
            self.url_beforenewsinfo_map[SQLDAO.SPIDER_TABLE_NEWS_CMTNUM][urlmd5] = value[max(value)]
        for urlmd5, value in clicknumlist.iteritems():
            if not value:
                continue            
            self.url_beforenewsinfo_map[SQLDAO.SPIDER_TABLE_NEWS_CLICKNUM][urlmd5] = value[max(value)]
        for urlmd5, value in votenumlist.iteritems():
            if not value:
                continue            
            self.url_beforenewsinfo_map[SQLDAO.SPIDER_TABLE_NEWS_VOTENUM][urlmd5] = value[max(value)]   
        for urlmd5, value in fansnumlist.iteritems():
            if not value:
                continue            
            self.url_beforenewsinfo_map[SQLDAO.SPIDER_TABLE_NEWS_FANSNUM][urlmd5] = value[max(value)]      
            
    #----------------------------------------------------------------------
    def aggregate_beforenewsnum(self):
        #计算url本次之前已经推送过的次数
        #如果key1标记为1,则表示该url对应的news id已经推送过；否则表示未推送过
        sqlf = 'SELECT {url},count(*) from {table} where {key1}=1 group by {url}'
        sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_NEWS,
                          url=SQLDAO.SPIDER_TABLE_NEWS_URL,
                          key1=SQLDAO.SPIDER_TABLE_NEWS_KEY1)   
        results = SQLDAO.getinstance().execute(sql, find=True)
        for result in results:
            key = Common.md5(result[0].strip())
            if key not in self.url_beforenewsnum_map:
                self.url_beforenewsnum_map[key] = int(result[1])         
    #----------------------------------------------------------------------
    def updatenewsflag(self, idlist):
        if idlist:
            idlist = [item.encode(constant.CHARSET_UTF8) for item in idlist]
            sqlf = 'UPDATE {table} SET {key1}=1  WHERE {key1} is null and {id} in {idlist}'
            sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_NEWS,
                              key1=SQLDAO.SPIDER_TABLE_NEWS_KEY1,
                              id=SQLDAO.SPIDER_TABLE_NEWS_ID,
                              idlist=tuple(idlist))
            Logger.getlogging().info('UPDATE news SET key1=1 where key1 is null')
            SQLDAO.getinstance().execute(sql)
    #----------------------------------------------------------------------
    def updatecommentsflag(self, urllist):
        if urllist:
            urllist = [item.encode(constant.CHARSET_UTF8) for item in urllist]
            sqlf = 'UPDATE {table} SET {key1}=1  WHERE {key1} is null and {url} in {urllist}'
            sql = sqlf.format(table=SQLDAO.SPIDER_TABLE_COMMENTS,
                              key1=SQLDAO.SPIDER_TABLE_COMMENTS_KEY1,
                              url=SQLDAO.SPIDER_TABLE_COMMENTS_URL,
                              urllist=tuple(urllist))
            Logger.getlogging().info('UPDATE comments SET key1=1 where key1 is null')
            SQLDAO.getinstance().execute(sql)      

    #----------------------------------------------------------------------
    @staticmethod
    def strfilter(string):
        if not string:
            return ''
        replaces = ['\n', '\r', '\t', ' ']
        for replace in replaces:
            string = string.replace(replace, '')
        return string

if __name__ == '__main__':
    import sys
    reload(sys)
    Logger.getlogging().info('set encoding={charset}!'.format(charset=constant.CHARSET_UTF8))
    sys.setdefaultencoding(constant.CHARSET_UTF8)    
    FileFormat().fileformat()
    Logger.getlogging().info('FINISH')