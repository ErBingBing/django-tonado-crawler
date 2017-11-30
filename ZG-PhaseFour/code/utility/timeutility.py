#encoding=utf-8

#import os
#import sys
#os.chdir('..')
#sys.path.append(os.getcwd())
import time
import re
from dateutil import parser
from datetime import datetime, timedelta
import traceback
########################################################################
class TimeUtility:
    """"""
    DEFAULTFORMAT  = '%Y-%m-%d %H:%M:%S'
    SQLTIMEFORMAT  = '%Y-%m-%d %H:%i:%S'
    DATE_FORMAT_DEFAULT = '%Y-%m-%d'
    TIMESTAMP_FORMAT = '%Y%m%d%H%M%S'
    # 2016-11-20 16:20:00
    TIME_FORMAT_DEFAULT = '%Y-%m-%d %H:%M:%S'
    # 2016-11-20T16:20:00+08：00
    UTC_FORMAT_DEFAULT  = '%Y-%m-%dT%H:%M:%S+08:00'
    
    BEFOREPATTERNS = [u'(\d+)\s*年\s*(\d+)\s*月\s*(\d*)\s*日',
                      u'(\d+)\s*月\s*(\d+)[日,\s.]*(\d+)\s*[年]?',
                             u'(\d+)\s*月\s*(\d*)\s*日',
                      u'(\d+)-(\d+)-?(\d*)',
                      u'(\d+)/(\d+)/?(\d*)']
    SECONDPATTERNS = [u'(\d+)\s*时\s*(\d+)\s*分\s*(\d*)\s*[秒]?',
                      u'(\d+):(\d+):?(\d*)\s?(AM|PM)?']
    
    UNNOMALFORMAT1 = {u'今天':{'days':0},
                      u'昨天':{'days':-1},
                      u'前天':{'days':-2},
                      u'一天前':{'days':-1},
                      u'两天前':{'days':-2},
                      u'三天前':{'days':-3},
                      u'一年前':{'days':-1*365},
                      u'两年前':{'days':-2*365},
                      u'三年前':{'days':-3*365},
                      u'刚刚':{'seconds':0},
                      u'半小时前':{'seconds':-30*60}
                      }
    
    UNNOMALFORMAT2 = {u'(\d+).*年前': {'days':-365},
                      u'(\d+).*月前': {'days':-30},
                      u'(\d+).*天前': {'days':-1},
                      u'(\d+).*小时前': {'hours':-1},
                      u'(\d+).*分钟前': {'seconds':-60},
                      u'(\d+).*秒前':{'seconds':-1}
                      }
    
    FLAGPATTERNS   = ['\n', '\t', '\r']
    
    #----------------------------------------------------------------------
    def __init__(self):
        pass
    
    """
        %y 两位数的年份表示（00-99）
        %Y 四位数的年份表示（000-9999）
        %m 月份（01-12）
        %d 月内中的一天（0-31）
        %H 24小时制小时数（0-23）
        %I 12小时制小时数（01-12）
        %M 分钟数（00=59）
        %S 秒（00-59）
        %a 本地简化星期名称
        %A 本地完整星期名称
        %b 本地简化的月份名称
        %B 本地完整的月份名称
        %c 本地相应的日期表示和时间表示
        %j 年内的一天（001-366）
        %p 本地A.M.或P.M.的等价符
        %U 一年中的星期数（00-53）星期天为星期的开始
        %w 星期（0-6），星期天为星期的开始
        %W 一年中的星期数（00-53）星期一为星期的开始
        %x 本地相应的日期表示
        %X 本地相应的时间表示
        %Z 当前时区的名称
        %% %号本身
    """
    ################################################################################################################
    # @functions：getuniformtime
    # @param： 任意格式的时间字符串
    # @param： 输入时间字符串格式
    # @return：返回标准时间格式的字符串
    # @note：获取标注的时间格式
    ################################################################################################################
    #----------------------------------------------------------------------
    @staticmethod
    def getuniformtime(string, format=DEFAULTFORMAT): 
        if isinstance(string, str):
            string = TimeUtility.strfilter(string)
        newstr = ''
        try:
            #***20160529212940***
            temp = string
            if re.search('\d{8,}', str(temp)):
                temp = re.findall('\d{8,}', temp)[0]                
                newstr = TimeUtility.getformattime(temp, format)
        except:
            pass
        try:       
            #时间戳
            if len(str(int(string))) == len(str(int(time.time()))) or \
               len(str(int(string)/1000)) == len(str(int(time.time()))) or \
               int(string) == 0:
                newstr = TimeUtility.getintformtime(string, format)
        except:
            pass
        if not newstr:
            newstr = TimeUtility.unnomalformat(string, format)
        if not newstr:
            newstr = TimeUtility.getformattime(string, format)
        if not newstr:
            newstr = TimeUtility.nomalformat(string, format)
        if not newstr:
            print u'Error: can\'t striptime {string}'.format(string=string)
        return newstr
    #----------------------------------------------------------------------
    @staticmethod
    def getformattime(string, format=DEFAULTFORMAT):
        if not string.strip():
            return TimeUtility.getintformtime(0)
        try:
            return datetime.strftime(parser.parse(string), format) 
        except:
            return None
    #----------------------------------------------------------------------
    @staticmethod
    def nomalformat(string, format=DEFAULTFORMAT):
        before = ''
        second = ''
        for pattern in TimeUtility.BEFOREPATTERNS:
            if re.search(pattern, string):
                numstr = re.findall(pattern, string)[0]
                numstr = [item for item in numstr if item]
                if len(numstr[-1]) > 4:
                    continue
                before = '-'.join(numstr)
                break
        for pattern in TimeUtility.SECONDPATTERNS:
            if re.search(pattern, string):
                numstr = re.findall(pattern, string)[0]
                numstr = [item for item in numstr if item]
                second = ':'.join(numstr)
                if numstr[-1]==u'AM' or numstr[-1]==u'PM':
                    second = ':'.join(numstr[:-1])+' '+numstr[-1]
                break
        newstr = before + ' ' +second
        return TimeUtility.getformattime(newstr, format)
    #----------------------------------------------------------------------
    @staticmethod
    def unnomalformat(string, format=DEFAULTFORMAT):     
        for pattern in TimeUtility.UNNOMALFORMAT1:
            if re.search(pattern, string):
                tempdict = TimeUtility.UNNOMALFORMAT1[pattern]
                newstr = (datetime.now() + timedelta(**tempdict)).strftime(format)
                if re.search(u'天', string):
                    second = TimeUtility.nomalformat(string)
                    if second:
                        newstr = newstr[:10] + ' ' +second[-8:]
                return TimeUtility.getformattime(newstr, format)
        for pattern in TimeUtility.UNNOMALFORMAT2:
            if re.search(pattern, string):
                tempint  = re.findall(pattern, string)[0]
                tempdict = TimeUtility.UNNOMALFORMAT2[pattern]
                tempkey  = tempdict.keys()[0]
                tempdict[tempkey] = tempdict[tempkey] * int(tempint)
                newstr = (datetime.now() + timedelta(**tempdict)).strftime(format)
                return TimeUtility.getformattime(newstr, format)

    #----------------------------------------------------------------------
    @staticmethod
    def getintformtime(inttime, format=DEFAULTFORMAT):
        if int(inttime) > 10000000000:
            inttime = int(inttime) / 1000
        return time.strftime(format, time.localtime(int(inttime)))
    
    #----------------------------------------------------------------------
    @staticmethod
    def getinttime(string, format=DEFAULTFORMAT):
        return time.mktime(time.strptime(string, format))
        
    #----------------------------------------------------------------------    
    @staticmethod
    def getcurrentdate(format=DATE_FORMAT_DEFAULT):
        return time.strftime(format)   
    #----------------------------------------------------------------------
    @staticmethod
    def getuniformdatebefore(delta, format=DEFAULTFORMAT):
        return TimeUtility.getuniformtime(str(datetime.now() - timedelta(days=int(delta))), format)

    #----------------------------------------------------------------------
    @staticmethod
    def getdatebefore(delta, format=DEFAULTFORMAT):
        return (datetime.now() - timedelta(days=int(delta))).strftime(format)
    #----------------------------------------------------------------------
    @staticmethod
    def strfilter(string):
        for flag in TimeUtility.FLAGPATTERNS:
            string = string.replace(flag, '').strip()
        return string
    ################################################################################################################
    # @functions：daycompare
    # @param： 时间t1,时间t2,时间比较的标准间隔
    # @return：True,False
    # @note：比较时间大小,t1-t2<=days
    ################################################################################################################
    @staticmethod
    def daycompare(t1, t2, days, format=DEFAULTFORMAT):
        if datetime.strptime(t1,format) - datetime.strptime(t2,format) <= timedelta(days):
            return True
        return False
    #----------------------------------------------------------------------
    @staticmethod
    def compareNow(curtime, days):
        """时间t比现在小多少天"""
        now = TimeUtility.getdatebefore(0)
        return TimeUtility.daycompare(now, curtime, days)
    #----------------------------------------------------------------------
    @staticmethod
    def isleap(year):
        is_leap = False
        if year % 100 == 0 and year % 400 == 0:
            is_leap = True
        elif year % 100 != 0 and year % 4 == 0:
            is_leap = True
        return is_leap
   
def test():
    print TimeUtility.getuniformtime('asdfgsdfgh月前')
    print TimeUtility.getuniformtime('<strong>天上的月饼</strong>发表于')
    print TimeUtility.getuniformtime(u'刚刚')
    print TimeUtility.getuniformtime(u'1秒前')
    print TimeUtility.getuniformtime(u'2016-11-22 22时14分11秒')
    print TimeUtility.getuniformtime(u'半小时前')
    print TimeUtility.getuniformtime(u'30分钟前')   
    print TimeUtility.getuniformtime(u'2016年11月10日 11:30:10')
    print TimeUtility.getuniformtime(u'谍影重重5幕后揭秘追车戏拍了一个多月栏目娱乐星天地标签谍影重重5,追车戏发布2016年11月10日 11:30:10')
    print TimeUtility.getuniformtime(u'猫眼电影   09-27 17:33   9457')
    print TimeUtility.getuniformtime(u'2016-10-8 18:57| 发布者: 阿狱| 查看: 164| 评论: 0')
    print TimeUtility.getuniformtime(1480132556)
    print TimeUtility.getuniformtime(u'20160529212940')
    print TimeUtility.getuniformtime(time.time())   
    print TimeUtility.getuniformtime(u'11月22日 22时14分13')
    print TimeUtility.getuniformtime(u'11月22日 22时14分')
    print TimeUtility.getuniformtime(u'一天前')
    print TimeUtility.getuniformtime(u'昨天')
    print TimeUtility.getuniformtime(u'  今天  22时14分')
    print TimeUtility.getuniformtime(u'  昨天  22时14分')
    print TimeUtility.getuniformtime(u'  前天  22时14分') 
    print TimeUtility.getuniformtime(u' 4 天前')
    print TimeUtility.getuniformtime(u'18小时前')
    print TimeUtility.getuniformtime(u'3分钟')
    print TimeUtility.getuniformtime(u'两年前') 
    #print TimeUtility.getuniformtime([u'1年前',u'2年前'])    
    print TimeUtility.getuniformtime(u'发表于2016-11-28 14:46')
    print TimeUtility.getuniformtime(u'发表于 2016-10-9 00:07')
    print TimeUtility.getuniformtime(u'11月11日 2016年')
    print TimeUtility.getuniformtime(u'11-01 2016 ')     
    print TimeUtility.getuniformtime(u'2016-11-28 14:46:58.753')
    print TimeUtility.getuniformtime(u'Sat Nov 26 13:00:09 2016')
    print TimeUtility.getuniformtime(u'2016-10-06 20:32:57.123')
    print TimeUtility.getuniformtime(u'2016/11/22 22:14:01')
    print TimeUtility.getuniformtime(u'2016-11-22')
    print TimeUtility.getuniformtime(u'2016年11月22日') 
    print TimeUtility.getuniformtime(u'2016/11/22 22时14分10') 
    print TimeUtility.getuniformtime(u'2016/11/22 22:14') 
    print TimeUtility.getuniformtime(u'2016-11-22 22时14分11')
    print TimeUtility.getuniformtime(u'2016年11月22日 22时14分12') 
    print TimeUtility.getuniformtime(u'阅读量201 2016-8-30 12:48| 发布者: Bo2| 查看: 13')
    print TimeUtility.getuniformtime(u'阅读量201 2016-12-14 22时14分3 阅读量2012')  
    print TimeUtility.getuniformtime(u'发布时间：2016年11月25日123123')
    print TimeUtility.getuniformtime(u'jsdkf2016/11/25 23123')
    print TimeUtility.getuniformtime(u'\n\t\t\t\t\n\t2016-11-5\n\tf233')
    print TimeUtility.getuniformtime('\n\t\t\t\t\n')
    print TimeUtility.getuniformtime(1459175064)
    print TimeUtility.getuniformtime(1479635286890)
    print TimeUtility.getuniformtime(u'Fri Jan 02 23:05:10 CST 2015')     

if __name__ == '__main__':       
    #test()
    #print TimeUtility.getuniformtime(u'发表于 2017-2-21 09:59 PM')
    #print TimeUtility.getuniformtime('1459175064')
    #print TimeUtility.getuniformtime(u'20160529212940')
    #print TimeUtility.getuniformtime(u'20170623：第11期：热巴Baby合体对撕外国猛男')
    print TimeUtility.getuniformtime(u'2016年09月21日19:47')
    print TimeUtility.getuniformtime(u'11月11日 2016年')
    print TimeUtility.getuniformtime(u'11-01 2016 ') 
    print TimeUtility.getuniformtime(u'11月11日 2016')
    print TimeUtility.getuniformtime(u'11月11日,2016')