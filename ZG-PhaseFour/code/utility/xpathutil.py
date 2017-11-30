# coding=utf8
################################################################################################################
# @file: xpathutil.py
# @author: JiangSiwei
# @date:  2016/11/25
# @version: Ver0.0.0.100
# @note: 
################################################################################################################
import urllib
from lxml import etree
import lxml
import re
import traceback
from  gettimeutil import getuniformtime 
#from log.spiderlog import Logger
import urllib

################################################################################################################
# @class：XPathUtility
# @author：JiangSiwei
# @date：2016/11/25
# @note：初始化参数为html.
#        方法：xpath,getlist,getstring
#        调用lxml.etree模块，实现获取含标签的文本内容
#        改进了原lxml.etree().xpath方法定位标签获取文本时，标签内含有其他标签而不能获取其全部文本的不足
################################################################################################################
from log.spiderlog import Logger


class XPathUtility:
    ################################################################################################################
    # @functions：__init__
    # @param： 传入参数：html
    # @return：
    # @note：lxml.etree初始化内部变量
    ################################################################################################################    
    def __init__(self, html=None, url=None):
        
        if url:
            respond=urllib.urlopen(url)                #可以更换此处的下载api
            html=respond.read()  
        if html:
            self.html = html                               #获取源码
            self.xHtml = etree.HTML(self.html)            
            
    ################################################################################################################
    # @functions:xpath
    # @param： 传入参数：xpath
    # @return：
    # @note：直接调用lxml.etree的方法xpath,等同lxml.etree().xpath方法
    ################################################################################################################       
    def xpath(self,xpath):
        if not xpath:
            return
        return self.xHtml.xpath(xpath)
    
    ################################################################################################################
    # @functions:getlist
    # @param： 传入参数：xpath
    # @return：文本序列
    # @note：调用lxml.etree的方法xpath,实现获取含标签的文本内容，返回参数为一个文本序列
    ################################################################################################################       
    def getlist(self, xpath):    
        if not xpath:
            return []        
        try:
            contents = self.xHtml.xpath(xpath)
            items =[]
            for item in contents:
                if type(item) == lxml.etree._Element:
                    items.append(item.xpath('string(.)').strip())
                if type(item) == lxml.etree._ElementUnicodeResult :
                    items.append(item.strip())
            return items            
        except:
            Logger.printexception()
            Logger.getlogging().error('xpath:{xpath} error'.format(xpath=xpath))
            return []
            
    ################################################################################################################
    # @functions:getstring
    # @param： 传入参数：xpath
    # @return：定位标签的所有内容
    # @note：调用lxml.etree的方法xpath,实现获取含标签的文本内容，返回参数为一个定位标签的所有内容
    ################################################################################################################         
    def getstring(self, xpath, slipt=''):
        items = self.getlist(xpath)
        contontStr = slipt.join(items)
        return contontStr
 
    ################################################################################################################
    # @functions:xpathlist
    # @param： 传入参数：固定分隔符的xpath
    # @return：定位标签的所有内容
    # @note：返回参数为多个定位标签的所有内容
    ################################################################################################################      
    def getstring2(self, xpath, split='|', join=''):
        contentlist = []
        items = xpath.split(split)
        for item in items:
            content = self.getstring(item, join)
            contentlist.append(content)
        return join.join(contentlist)
            
    '''获取标题'''
    def gettitle(self, xpath):
        title = self.getstring(xpath)
        if title:
            return title
        else:
            xpath = '/html/head/title'
            return self.getstring(xpath)


    '''获取时间(发布时间,抓取时间)'''
    def gettime(self, xpath):
        timetext= self.getstring(xpath)
        return getuniformtime(timetext)

    '''获取正文'''
    def getcontent(self, xpath):
        return self.getstring(xpath)

    '''获取评论'''
    def getcomments(self, xpath):
        return self.getlist(xpath)

    '''获取数量'''
    def getnumber(self, xpath):
        if not xpath:
            return 0
        try:
            numbertext = self.getstring(xpath)
            p1 = '(\d+[\.\d]*万|\d+[\.\d]*亿)'
            p2 = u'(\d+[\.\d]*[万亿])'
            if re.search(p1, numbertext) or re.search(p2, numbertext):
                if re.findall(p1, numbertext):
                    number = re.findall(p1, numbertext)[0]
                if re.findall(p2, numbertext):
                    number = re.findall(p2, numbertext)[0]
                if re.search('万', number) or re.search(u'万', number):
                    number = float(re.findall('\d+[\.\d]*', number)[0]) * 10000
                elif re.search('亿', number) or re.search(u'亿', number):
                    number = float(re.findall('\d+[\.\d]*', number)[0]) * 100000000              
                    
            elif re.search('\d+[\.\d]*', numbertext):
                number = re.findall('\d+[\.\d]*', numbertext)[0]
                number = float(number)
            else:
                number = 0
            return number
        except Exception:
            traceback.print_exc()
            return 0
   
   


            
if __name__ =='__main__':
    
    url='http://www.gameres.com/forum.php?mod=viewthread&tid=694567&extra=page%3D1&from=portal&page=3'
    html = urllib.urlopen(url).read()
    #from  bs4  import BeautifulSoup
    
    #soup = BeautifulSoup(html,'html5lib')
    #times = soup.find_all(attrs={'class':'xg1 xw0'})
    #for item in times:    
        #print getuniformtime(str(item))    
    #print html

    #path = r'C:\Users\IT8000\Downloads\temp\temp\http%3A__www.2200book.com_files_article_info_104_104298.htm'
    #f= open(path,'r')
    #html = f.read()
    #f.close()

    #times = xparser.getlist('//*[@class="xg1 xw0" and text()]|//*[@class="xg1 xw0"]/span/@title')
    #print times
    #times = [ getuniformtime(i)  for i in times]
    #print times
    
    #ll = ['//h1',
    #'//*[contains(@id,"post")]',
    #'//*[@class="hm"]/span[4]',
    #'//*[@class="hm"]/span[2]',
    #'//*[contains(@id,"authorposton")]']
    #for item in ll:
        #print xhtml.getstring(item)
    #print xhtml.html
    #print xhtml.gettitle('//*[@id="thread_subject"]')
    #print xhtml.getlist('//*[@class="long-pages"]/a')[-2]
    #print xhtml.getcontent('//*[@class="bbs-content clearfix"]')
    #print xhtml.xpath('//*[@class="atl-content"]')[0].xpath('//*[@class="bbs-content"]/text()')
    
