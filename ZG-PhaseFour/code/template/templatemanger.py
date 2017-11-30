# encoding=utf-8
##############################################################################################
# @file：spiderdao.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：berkeley db interface
##############################################################r################################


import json
from utility.regexutil import RegexUtility
from log.spiderlog import Logger


class TemplateManager:
    XPATH_KEY_URL_TEMPLATE = 'template'
    XPATH_KEY_WEBURL = 'website_url'
    XPATH_KEY_TITLE = 'title'
    XPATH_KEY_BODY = 'body'
    XPATH_KEY_COMMENTS_NUM = 'cmtnum'
    XPATH_KEY_CLICK_NUM = 'clicknum'
    XPATH_KEY_VOTE_NUM = 'votenum'
    XPATH_KEY_FANS_NUM = 'fansnum'
    XPATH_KEY_PUBLISH_TIME = 'pubtime'

    __instance = None

    def __init__(self):
        self.listtemplates = {}
        self.nlisttemplates = []
        self.templatespath = './resources/patterns.json'
        self.re = RegexUtility
        self.urlcount = 0
        self.urlnotemplate = 0

    def __getxpaths(self, url):
        domain = TemplateManager.getdomain(url)
        if domain and domain in self.listtemplates:
            return self.__getxpaths__(url, self.listtemplates[domain])
        else:
            return self.__getxpaths__(url, self.nlisttemplates)

    def __getxpaths__(self, url, listtemplates):
        self.urlcount += 1
        templates = []
        for template in listtemplates:
            if RegexUtility.match(template[TemplateManager.XPATH_KEY_URL_TEMPLATE] + '\S*', url):
                templates.append(template)
                break
        if templates:
            if len(templates) > 1:
                Logger.getlogging().warning('More than one template found for %s' % url)
            return templates
        else:
            self.urlnotemplate += 1
            Logger.getlogging().warning('No template found for %s' % url)
            Logger.getlogging().warning('No template found %d/%d' % (self.urlnotemplate, self.urlcount))
        return []

    def __loadxpaths(self):
        with open(self.templatespath, 'r') as fp:
            for line in fp.readlines():
                template = json.loads(line.strip())
                if len(template[TemplateManager.XPATH_KEY_URL_TEMPLATE].strip()) > 0:
                    domain = TemplateManager.getdomain(template[TemplateManager.XPATH_KEY_WEBURL])
                    if domain:
                        if domain not in self.listtemplates:
                            self.listtemplates[domain] = []
                        self.listtemplates[domain].append(template)
                    else:
                        self.nlisttemplates.append(template)

    @staticmethod
    def getxpaths(url):
        return TemplateManager.getinstance().__getxpaths(url)

    @staticmethod
    def getinstance():
        if TemplateManager.__instance is None:
            TemplateManager.__instance = TemplateManager()
            TemplateManager.__instance.__loadxpaths()
        return TemplateManager.__instance

    NOMEANS_VALUES = ['com', 'cn', 'org', 'net']

    @staticmethod
    def getdomain(url):
        array = url.split('/')
        if len(array) < 3:
            return ''
        array = array[2].split('.')
        index = len(array) - 1
        domain = ''
        while index >= 0:
            if array[index] in TemplateManager.NOMEANS_VALUES:
                index -= 1
                continue
            else:
                domain = array[index]
                break
        return domain


import os
if __name__ == '__main__':
    os.chdir('..')
    urls = [
    'http://kid.qq.com/a/20161001/003936.htm#p=1',
    'http://tech.qq.com/a/20161008/003207.htm',
    'http://baby.qq.com/a/20161008/010464.htm']
    for url in urls:
        print TemplateManager.getxpaths(url)


