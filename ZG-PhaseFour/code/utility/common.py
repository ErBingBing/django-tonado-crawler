# encoding=utf-8
##############################################################################################
# @file：common.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：共通方法
##############################################################r################################
import hashlib
import re
from urllib import quote
from urllib import unquote
from configuration import constant
from configuration.constant import CHARSET_UTF8, CHARSET_GBK


################################################################################################################
# @class：Common
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：
################################################################################################################
class Common:
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        return

    ################################################################################################################
    # @functions：url2md5
    # @param： channel
    # @param： query
    # @param： url
    # @return：md5
    # @note：根据channel、query、url获取MD5
    ################################################################################################################
    @staticmethod
    def url2md5(channel, query, url):
        return Common.md5('{channel}_{query}_{url}'.format(
            channel=channel.strip(),
            query=query.strip(),
            url=url.strip()))

    ################################################################################################################
    # @functions：md5
    # @param： 字符串
    # @return：md5
    # @note：计算字符串value的MD5
    ################################################################################################################
    @staticmethod
    def md5(value):
        m2 = hashlib.md5()
        m2.update(value)
        return m2.hexdigest()

    ################################################################################################################
    # @functions：urlenc
    # @param： info
    # @return：URL编码后的字符串
    # @note：URL编码
    ################################################################################################################
    @staticmethod
    def urlenc(info):
        return quote(str(info))

    ################################################################################################################
    # @functions：urldec
    # @param： URL编码的字符串
    # @return：URL解码后的字符串
    # @note：URL解码
    ################################################################################################################
    @staticmethod
    def urldec(info):
        return unquote(str(info))

    ################################################################################################################
    # @functions：utf2gbk
    # @param： utf8编码的字符串
    # @return：gbk编码的字符串
    # @note：utf8转gbk
    ################################################################################################################
    @staticmethod
    def utf2gbk(utf):
        return utf.decode(CHARSET_UTF8).encode(CHARSET_GBK)

    ################################################################################################################
    # @functions：gbk2utf
    # @param： gbk编码的字符串
    # @return：utf8编码的字符串
    # @note：gbk转utf8
    ################################################################################################################
    @staticmethod
    def gbk2utf(utf):
        return utf.decode(CHARSET_GBK).encode(CHARSET_UTF8)

    ################################################################################################################
    # @functions：strip
    # @param： 要处理字符串
    # @return：strip后的字符串，并删除换行
    # @note：strip，如果#开头的返回空字符串
    ################################################################################################################
    @staticmethod
    def strip(str):
        str = str.replace('\n', '').strip()
        if len(str) > 0 and str[0] == '#':
            str = ''
        return str

    @staticmethod
    def trydecode(str, charset=None):
        result = None
        other = None
        if not charset or charset.lower() == constant.CHARSET_UTF8:
            charset = constant.CHARSET_UTF8
            other = constant.CHARSET_GBK
        else:
            charset = constant.CHARSET_GBK
            other = constant.CHARSET_UTF8
        try:
            result = str.decode(charset)
        except:
            pass
        if not result:
            try:
                result = str.decode(other)
            except:
                pass
        # using default igonore to decode
        if not result:
            result = str.decode(charset, 'ignore')
        if not result:
            result = str
        return result

    ################################################################################################################
    # @functions：checktitle
    # @query：要检查的查询关键字
    # @title：检查对象字符串
    # @return：True 标题中包含所有的关键字 否则返回False
    # @note：
    ################################################################################################################
    @staticmethod
    def checktitle(query, title):
        query = Common.trydecode(query)
        title = Common.trydecode(title)
        ret = True
        keys = query.split(' ')
        for index in range(0, len(keys), 1):
            if title.lower().find(keys[index].lower()) < 0:
                ret = False
                break
        return ret

    @staticmethod
    def float2percent(value):
        return '%.2f%%' % (value * 100)
    
    @staticmethod
    def strfilter(s):
        spicial = ['\n','\r','\t']
        for s1 in spicial:
            s = s.replace(s1,' ').strip()   
        s = Common.remove_emoji(s)
        if 'document.write' in s:
            s = s[:s.index('document.write')]
        return s
    
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
        "+", flags=re.UNICODE)
    @staticmethod
    def remove_emoji(text):
        return Common.emoji_pattern.sub(r'', text)