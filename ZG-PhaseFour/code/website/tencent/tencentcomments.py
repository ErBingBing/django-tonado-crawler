 # encoding=utf-8

#################################################################################
# @class：TencentComments
# @author：JiangSiwei
# @date：2016/11/17
# @note：腾讯获取评论的文件，继承于SiteComments类
#################################################################################
import re
import json
import math
import time
from utility.timeutility import TimeUtility
from website.common.comments import SiteComments
from website.sohu.sohucomments import SohuComments
from storage.cmtstorage import CMTStorage
from storage.newsstorage import NewsStorage
from utility.bbs2commom import CommenComments
from log.spiderlog import Logger
from bs4 import BeautifulSoup
from utility.xpathutil import XPathUtility
from  lxml import etree
from bs4 import BeautifulSoup
from utility.gettimeutil import getuniformtime
from utility.common import Common
from configuration import constant 
from configuration.environment.configure import SpiderConfigure

class TencentComments(SiteComments):
    def __init__(self):
        SiteComments.__init__(self)
        self.page_size = 50
        self.page_size_yunqi = 10
        self.COMMENTS_URL = 'http://coral.qq.com/article/{0}/comment?commentid={1}&reqnum={2}'
        # self.AC_COMMENTS_URL = 'http://ac.qq.com/Community/topicList?targetId={0}&page={1}&type=0&_={2}'
        self.AC_COMMENTS_URL = 'http://ac.qq.com/Community/topicList?targetId={0}&page={1}'
        self.EBOOK_COMMENTS_URL = 'http://ebook.qq.com/{site}/getComment.html?bid={bid}&pageIndex={page}'
        self.YUNQI_COMMENT_URL ='http://yunqi.qq.com/bk/gdyq/%s-b.html?hot=0&p=%d'
        self.STEP_DEFAULT_VALUE = None
        self.STEP_COMMENT_FIRST_PAGE = 1
        self.STEP_COMMENT_NEXT_PAGE = 2          
        self.hasnext = True
        self.cmtlastdays = TimeUtility.getuniformdatebefore(int(SpiderConfigure.getinstance().getlastdays()))
        self.comment_maxnum = 5000
    ##############################################################################################
    # @functions：process
    # @param：共通模块传入的参数（原始url及其html,step参数，自定义参数）
    # @return: Step1：获取评论的首页url
    #          Step2：获取评论的所有url,抽出的评论和最新评论的创建时间
    # @author：
    # @date：
    # @note:: Step1:如果为腾讯动漫频道
    #               如果为腾讯视频网站，则必须先通过originalurl获取到能获取comment_id的url,并传递给共通模块，通过获取html中得到comment_id及url_id
    #               如果为腾讯新闻类网站，则通过共通模块传入的html内容获取到url_id，拼出获取评论总数的url，并传递给共通模块

    #         Step2:通过共通模块传入的html内容获取到评论和最新评论的创建时间，并传递给共通模块
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则保存最新更新时间
    #               如果上一次更新时间大于或等于最新更新时间，则数据已保存，不需要抓取；否则抓取新增的数据
    #               通过共通模块传入的html内容获取到评论总数及url_id，拼出获取评论的url，并传递给共通模块
    ##############################################################################################        

    def process(self, params):

        """
        1.适用在腾讯新闻及其他部分
        2.适用在腾讯视频部分https://v.qq.com/
        3.适用在腾讯动漫视频部分http://ac.qq.com/Comic/
        4.适用在腾讯QQ阅读部分http://ebook.qq.com/
        5.适用在腾讯云起书城http://yunqi.qq.com/
        """

        if self.r.search('^http[s]{0,1}://ac\.qq\.com/Comic/.*',params.originalurl):
            if params.step == self.STEP_DEFAULT_VALUE:
                self.step1_ac(params)
            elif params.step == self.STEP_COMMENT_FIRST_PAGE:
                self.step2_ac(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step3_ac(params)
        elif self.r.search('^http[s]{0,1}://v\.qq\.com/.*',params.originalurl):
            if params.step == self.STEP_DEFAULT_VALUE:
                self.get_url_id(params)
            elif params.step == self.STEP_COMMENT_FIRST_PAGE:
                self.step1(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step2(params)
        elif self.r.search('^http[s]{0,1}://bbs\.book\.qq\.com/.*',params.originalurl):
            CommenComments(self).process(params)
        elif self.r.search('^http[s]{0,1}://ebook\.qq\.com/.*',params.originalurl):
            if params.step == self.STEP_DEFAULT_VALUE:
                self.step1_ebook(params)
            elif params.step == self.STEP_COMMENT_FIRST_PAGE:
                self.step2_ebook(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step3_ebook(params)
        elif self.r.search('^http[s]{0,1}://yunqi\.qq\.com/.*',params.originalurl):
            if params.step == self.STEP_DEFAULT_VALUE:
                self.step1_yunqi(params)
            elif params.step == self.STEP_COMMENT_FIRST_PAGE:
                self.step2_yunqi(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step3_yunqi(params)
        elif self.r.search('^http[s]{0,1}://p\.weather\.com\.cn.*',params.originalurl):
            SohuComments(self).process(params)
        else:
            if params.step == self.STEP_DEFAULT_VALUE:
                self.step1(params)
            elif params.step == self.STEP_COMMENT_NEXT_PAGE:
                self.step2(params)

    ################################################################################################################
    # 腾讯视频
    #
    # @functions：step1
    # @params： params
    # @return：none
    # @note：获取url_id关键字
    #
    # @functions：step2
    # @params： params
    # @return：none
    # @note：获取评论的其他url,及评论
    ################################################################################################################
    #----------------------------------------------------------------------
    #@staticmethod
    #def get_v_oriurl(params):
        #pattern = 'https?://v\.qq\.com/x/cover/(\w+)/?\w*\.html'
        #if re.search(pattern, params.originalurl):
            #return 'https://v.qq.com/x/cover/'+re.findall(pattern, params.originalurl)[0]+'.html'
        #else: 
            #return params.originalurl
    def step1(self, params):
        """获取评论的首页url"""
        try:
            #获取上一次的最新更新时间
            before_update = CMTStorage.getlastpublish(params.originalurl)
            #获取其他信息，拼接url
            url_id = None
            if self.r.search('^http[s]{0,1}://v\.qq\.com/.*', params.originalurl):
                #{"comment_id":"1167760750","result":{"code":0,"msg":"Success!","ret":0},"srcid":"c0016r7fo07","srcid_type":1001}
                url_id  = self.r.getid('comment_id', params.content)           
            else:
                url_id = self.r.getid('cmt_id', params.content)
                if not url_id:
                    url_id = self.r.getid('aid', params.content)
                if not url_id:
                    url_id = self.r.getid('commId', params.content)
            if url_id:
                comment_url = self.COMMENTS_URL.format(url_id, 0, self.page_size)
                self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE,
                              {'url_id': url_id, 'comment_id': 0,
                               'before_update':before_update})
        except:
            Logger.printexception()

    def step2(self, params):
        """获取评论的其他url,及评论"""
        #每次spider运行的累加数据tempcmttotal
        #
        try:
            url_id = params.customized['url_id']
            comment_id = params.customized['comment_id']
            before_update = params.customized['before_update']
            tempcmttotal = params.customized.get('tempcmttotal',0)
            try:
                jsondata = json.loads(params.content)
                last = jsondata['data']['last']
                hasnext = jsondata['data']['hasnext']
                cmttotal= float(jsondata['data']['total'])
                NewsStorage.setcmtnum(params.originalurl, cmttotal)
            except:
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
                return
            temptimes = []
            for comment in jsondata['data']['commentid']:
                tempcmttotal += 1
                content = comment['content']
                time = TimeUtility.getuniformtime(comment['time'])
                temptimes.append(time)
                user = comment['userinfo'].get('nick','anonymous')
                # 保存评论到数据库，可以通过接口exist判断评论是否已经存在
                CMTStorage.storecmt(params.originalurl, content, time, user)
            #对是否继续提取评论进行条件限制
            nextflag = True
            if temptimes:
                min_update = min(temptimes)
                max_update = max(temptimes)
                #发布时间临界点限制:最近两天
                #if max_update < self.cmtlastdays:
                    #nextflag = False
                #发布时间限制:仅针对qq的评论提取策略，该评论的发布时间有序且依次递减
                if min_update < before_update:
                    nextflag = False
            #数量限制
            if tempcmttotal >= self.comment_maxnum:
                nextflag = False
            if float(tempcmttotal)/self.page_size > self.maxpages:
                nextflag = False
            if hasnext and nextflag:
                url = self.COMMENTS_URL.format(url_id, last, self.page_size)
                self.storeurl(url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE,
                              {'url_id': url_id, 'comment_id': last, 'before_update':before_update, 'tempcmttotal':tempcmttotal})
        except:
            Logger.printexception()
    ################################################################################################################
    # @functions：step1_ac
    # @params： params
    # @return：none
    # @note：获取评论的首页url(只适用在腾讯动漫视频部分)
    #
    # @functions：step2_ac
    # @params： params
    # @return：none
    # @note：获取评论的其他url,及评论(只适用在腾讯动漫视频部分)
    #
    # @functions：step3_ac
    # @params： params
    # @return：none
    # @note：
    ################################################################################################################

    def step1_ac(self,params):
        """只适用在腾讯动漫视频部分，获取评论的首页url"""
        #if self.r.search('^http://ac\.qq\.com/Comic/.*',params.originalurl):
        url_id = self.r.parse('id/(\d+)',params.originalurl)[0]
        # millis = int(round(time.time() * 1000))
        comment_url = self.AC_COMMENTS_URL.format(url_id,1)
        print comment_url
        self.storeurl(comment_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'url_id':url_id})

    def  step2_ac(self,params):
        """只适用在腾讯动漫视频部分,获取评论的url列表"""
        url_id = params.customized['url_id']
        xhtml = etree.HTML(params.content)
        # 评论数量获取经常会参数错误
        comments_count = xhtml.xpath('//*[@id="pagination-node"]/span/em/text()')
        if comments_count:
            comments_count = int(comments_count[0])
        else:
            Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
            return
        page_size = len(xhtml.xpath('//*[@class="comment-content-detail"]'))
        # 判断增量
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        NewsStorage.setcmtnum(params.originalurl, comments_count)
        if cmtnum >= comments_count:
            return
    
        page_num=int(math.ceil((float(comments_count)/page_size)))
        if int(page_num) >= self.maxpages:
            page_num = self.maxpages
        for page in range(1,page_num+1):
            url = self.AC_COMMENTS_URL.format(url_id,page)
            self.storeurl(url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE)

    def step3_ac(self,params):
        """获取评论"""
        try:
            xhtml = etree.HTML(params.content)
            commentlist = xhtml.xpath('//*[@class="comment-content-detail"]')
            timelist =xhtml.xpath('//*[@id="commen-con"]/div/div[2]/div[2]/span[3]')
            nicklist = xhtml.xpath('//*[@class="comment-content-name"]')
            if len(commentlist) == len(timelist):
                for i in range(len(timelist)):
                    content = commentlist[i].text.strip()
                    curtime = TimeUtility.getuniformtime(timelist[i].text+':00')
                    nick = nicklist[i].text.strip()
                    if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                        CMTStorage.storecmt(params.originalurl, content, curtime, nick)
        except:
            Logger.printexception()
            Logger.getlogging().error('extract comment error from {site}'.format(site = params.originalurl))

    ################################################################################################################
    # @functions：step1_ebook
    # @params： params
    # @return：none
    # @note：获取bid关键字
    #
    # @functions：step2_ebook
    # @params： params
    # @return：none
    # @note：获取评论的其他url,及评论(只适用在QQ阅读部分)
    #
    # @functions：step3_ebook
    # @params： params
    # @return：none
    # @note：获取评论(只适用在QQ阅读部分)
    ################################################################################################################

    def step1_ebook(self, params):
        try:
            bid = self.r.parse('^http://ebook\.qq\.com\/.*\.html\?bid=(\d+)', params.originalurl)[0]
            commentinfo_url = self.EBOOK_COMMENTS_URL.format(site='intro' ,bid=bid ,page=1)
            self.storeurl(commentinfo_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE,{'bid':bid})
        except Exception,e:
            Logger.printexception()

    def step2_ebook(self, params):
        try:
            #"""只适用在QQ阅读部分,获取评论的url列表"""
            bid = params.customized['bid']
            jsoncontent = json.loads(params.content)
            if not jsoncontent.has_key('data'):
                Logger.log(params.originalurl, constant.ERRORCODE_SITE_NOGET_COMMNETS)
                return
            comments_count = jsoncontent['data']['total']
            page_count = jsoncontent['data']['pageCount']
            # 判断增量
            cmtnum = CMTStorage.getcount(params.originalurl,True)
            NewsStorage.setcmtnum(params.originalurl, comments_count)
            if cmtnum >= comments_count:
                return
    
            # 判断10页
            if int(page_count) >= self.maxpages:
                page_count = self.maxpages

            for page in range(1, page_count + 1, 1):
                commentinfo_url = self.EBOOK_COMMENTS_URL.format(site='intro' ,bid=bid ,page=page)
                self.storeurl(commentinfo_url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE)
        except Exception,e:
            Logger.printexception()

    def step3_ebook(self, params):
        try:
            jsoncontent = json.loads(params.content)
            if not jsoncontent.has_key('data'):
                return
            html = jsoncontent['data']['listHtml']
            if not html:
                return
            soup = BeautifulSoup(html,'lxml')
            divs = soup.select('div.cf')
            if not divs:
                return
            for div in divs:
                # commentList > dl:nth-child(1) > div.cf > dd > p:nth-child(2)
                content = div.select('dd > p')[1].get_text()

                curtime = TimeUtility.getuniformtime(div.select('dd > p')[0].get_text().split('|')[-1])
                nick = div.select('dd > p')[0].get_text().split('|')[0]

                if not CMTStorage.exist(params.originalurl, content, curtime, nick):
                    CMTStorage.storecmt(params.originalurl, content, curtime, nick)

        except Exception, e:
            Logger.printexception()

    ################################################################################################################
    # @functions：step1_yunqi
    # @params： params
    # @return：none
    # @note：获取评论(只适用在云起书城部分)
    #
    # @functions：step2_yunqi
    # @params： params
    # @return：none
    # @note：获取评论(只适用在云起书城部分)
    #
    # @functions：step3_yunqi
    # @params： params
    # @return：none
    # @note：获取评论(只适用在云起书城部分)
    ################################################################################################################

    def step1_yunqi(self, params):
        #Step1: 通过得到docurl，得到获取评论的首页url参数。
        articleId = self.r.parse('http://yunqi\.qq\.com/bk/\w+/(\d+).html', params.originalurl)[0]
        # 取得评论的url列表
        comments_url = self.YUNQI_COMMENT_URL % (articleId, 1)
        self.storeurl(comments_url, params.originalurl, self.STEP_COMMENT_FIRST_PAGE, {'articleId': articleId})

    def step2_yunqi(self, params):
        # 获得评论参数
        articleId = params.customized['articleId']
        # 取得总件数
        page = int(XPathUtility(params.content).getnumber('//*[@class="Pagination"]/em'))
        curcmtnum = (page - 1) * self.page_size_yunqi 
        NewsStorage.setcmtnum(params.originalurl, curcmtnum + self.page_size_yunqi/2)
        cmtnum = CMTStorage.getcount(params.originalurl,True)
        if curcmtnum < cmtnum:
            return
        page = int(math.ceil(float(curcmtnum+self.page_size_yunqi/2-cmtnum)/self.page_size_yunqi))
        if page >= self.maxpages:
            page = self.maxpages
        # 获得url列表
        for pg in range(1, page + 1, 1):
            url = self.YUNQI_COMMENT_URL % (articleId, pg)
            self.storeurl(url, params.originalurl, self.STEP_COMMENT_NEXT_PAGE)

    def step3_yunqi(self, params):
        # Step3: 通过Step2设置的url，得到所有评论，抽取评论
        # 取得所有评论
        soup = BeautifulSoup(params.content, 'html5lib')
        comments = soup.select('#commentList> li')
        for comment in comments:
            try:
                content = comment.select_one('.textBox').get_text()
                curtime = comment.select_one('.userName > span').get_text()
                CMTStorage.storecmt(params.originalurl, content, curtime, '')
            except:
                Logger.printexception()
                
    ################################################################################################################
    # @functions：get_url_id
    # @params： params
    # @return：none
    # @note：通过解析传回的html页面获取vid/cid，以便拼出step1中获取评论的url_id的url。(只适用在腾讯视频的部分)
    ################################################################################################################
    def get_url_id(self,params):

        """只适用在腾讯视频的部分"""
        "cid是电视剧\合集\电影,vid单集"
        CID_PATTERN = 'https?://v\.qq\.com/x/cover/(\w+).html'
        CID_URL='https://ncgi.video.qq.com/fcgi-bin/video_comment_id?otype=json&op=3&cid={cid}'
        VID_PATTERN1 = 'https?://v\.qq\.com/x/cover/\w+/(\w+).html'
        VID_PATTERN2 = 'https?://v\.qq\.com/x/page/(\w+)\.html'
        VID_URL='https://ncgi.video.qq.com/fcgi-bin/video_comment_id?otype=json&op=3&vid={vid}'
        
        if self.r.search(CID_PATTERN, params.originalurl):
            cid = self.r.parse(CID_PATTERN, params.originalurl)[0]
            url = CID_URL.format(cid=cid)
            self.storeurl(url, params.originalurl,self.STEP_COMMENT_FIRST_PAGE)
        elif self.r.search(VID_PATTERN1, params.originalurl):
            vid = self.r.parse(VID_PATTERN1, params.originalurl)[0]
            url = VID_URL.format(vid=vid)
            self.storeurl(url, params.originalurl,self.STEP_COMMENT_FIRST_PAGE)
        elif self.r.search(VID_PATTERN2, params.originalurl):
            vid = self.r.parse(VID_PATTERN2, params.originalurl)[0]
            url = VID_URL.format(vid=vid)
            self.storeurl(url, params.originalurl,self.STEP_COMMENT_FIRST_PAGE)        
        #publish_date
        publish_date = self.r.getid('publish_date', params.content, split=':')
        if not publish_date:
            publish_date = XPathUtility(params.content).getstring('//*[@class="video_tags"]/span|//*[@class="date"]|//*[@class="tag_item"]')
            publish_date = TimeUtility.getuniformtime(publish_date)
        if publish_date:
            NewsStorage.setpublishdate(params.originalurl, publish_date)
        self.setclick(params)

    def setclick(self, params):
        soup = BeautifulSoup(params.content,'html5lib')
        #电视剧
        itemcount = soup.select('.mod_episode > .item')
        if itemcount:
            total = self.str2num(soup.select_one('#mod_cover_playnum').get_text())
            clicknum = total / len(itemcount)
            NewsStorage.setclicknum(params.originalurl,clicknum)  
            return
        #其他
        parentid = params.originalurl.split('.')[-2].split('/')[-1]
        #figures_list = soup.find_all(attrs={'class':re.compile('^figures?_list$')})
        for fitem in soup.find_all(attrs={'class':re.compile('^figures?_list$')}):
            #list_items = fitem.find_all(attrs={'class':re.compile('list_item')})
            for item in fitem.find_all(attrs={'class':re.compile('list_item')}):
                childurl = item.select_one('a').get('href', None)
                childid=  childurl.split('.')[-2].split('/')[-1]
                #Logger.getlogging().debug('childid:'+childid+'\t'+'parentid:'+parentid)
                if childid == parentid:
                    numobj = item.find(attrs={'class':re.compile('num _video_playnum|figure_num')})
                    if not numobj:
                        continue
                    clicknum = self.str2num(numobj.get_text())
                    NewsStorage.setclicknum(params.originalurl,clicknum)
                    return
