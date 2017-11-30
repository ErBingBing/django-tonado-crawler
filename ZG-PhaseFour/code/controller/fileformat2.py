# -*- coding: utf-8 -*-

import re
import json
from dao.channeldao import ChannelDao
from dao.mongodao import MongoDAO

TEMPSITEMAP = {'shangdong':'sd','zj':'zhejiang'}

class Site:
    #SITEDICT = {}
    def __init__(self):
        filename = r'E:\jiang\T-WENZHI\local\spider\resources\s3websites_info.json'
        self.sitedict = Site.getsitedict(filename)
        pass
    
    @staticmethod
    def getsiteid(url):
        pattern1= 'https?://.*\.(\w+)\.{domain}\.{fix}/?'
        pattern2= 'https?://(\w+)\.{domain}\.{fix}/?'
        new = ['.org','.net','.me','.com','.cn']
        newstring = '{web}.{domain}.{fix}'    
        for fix in new:
            if fix in url:
                sufix = url.split(fix)[0]
                domain = sufix.split('.')[-1]
                if domain.startswith('http://'):
                    web = domain.split('//')[-1].split('.')[-1]
                    domain = url.split(domain)[-1].strip('.').split('.')[0]
                    break
                patterns = [pattern1.format(domain=domain,fix=fix.split('.')[-1]),
                            pattern2.format(domain=domain,fix=fix.split('.')[-1])]
                for pattern in patterns:
                    if re.search(pattern,url):
                        web = re.findall(pattern,url)[0]
                        break
                else:
                    print '{url} can\'t get the website'.format(url=url)
                    web = ''
                break
        return newstring.format(web=web,domain=domain,fix=fix.split('.')[-1])
    
    @staticmethod
    def getsitedict(filename):
        SITEDICT = {}
        with open(filename, 'r') as fp:
            lines = fp.readlines()         
        for line in lines:
            line = json.loads(line)
            url = line['url']
            cid = str(int(line['cid']))
            web,site,fix=Site.getsiteid(url).split('.')
            if site not in SITEDICT:
                SITEDICT[site] = {}
            SITEDICT[site][web]=cid
        print SITEDICT
        return SITEDICT
           
    def getcid(self,url):
        web,site,fix = Site.getsiteid(url).split('.')
        if web in TEMPSITEMAP:
            web = TEMPSITEMAP[web]
        if site in self.sitedict:
            webs = self.sitedict[site]
            if len(webs) == 1:
                cid = webs.values()[0]
            elif web in webs:
                cid = webs[web]
            elif 'www' in webs:
                cid = webs['www']
            else:
                cid = '000'
        else:
            print '{url} can\'t find the site cid'.format(url=url)
            cid = '000'
        return cid
    
class Fileformat:
    def __init__(self):
        self.site = Site()
    
        
        
if __name__ == '__main__':
    site = Site()
    print site.getcid('http://news.sina.com.cn/gov/2017-07-12/doc-ifyhwehx5783917.shtml')