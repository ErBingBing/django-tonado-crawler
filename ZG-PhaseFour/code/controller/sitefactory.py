# -*- coding: utf-8 -*-
###################################################################################################
# @file: sitefactory.py
# @author: Sun Xinghua
# @date:  2016/11/21 0:15
# @version: Ver0.0.0.100
# @note:
###################################################################################################
from log.spiderlog import Logger
from template.templatemanger import TemplateManager
from website.common.site import WebSite


from website.acfun.acfun import AcFun
from website.acg7.sevenAcg import SevenAcg
from website.actoys.actoys import Actoys
from website.adquan.adquan import Adquan
from website.angeeks.angeeks import Angeeks
from website.appgame.appgame import Appgame
from website.baidu.baidu import Baidu
from website.baozou.baozou import BaoZou
from website.bilibili.bilibili import Bilibili
from website.cn21.Cn21 import Cn21
from website.china.china import China
from website.dm78.dm78 import Dm78
from website.dmzj.dmzj import Dmzj
from website.domarketing.main import domarketing
from website.donews.donews import DoNews
from website.douban.douban import douban
from website.duowan.duowan import Duowan
from website.edugov.edugov import Edugov
from website.fun.fun import Fun
from website.game3dm.game3dm import Game3dm
from website.gamelook.main import gamelook
from website.gameres.gameres import Gameres
from website.gametanzi.gametanzi import Gametanzi
from website.gao7.main import gao7
from website.gfan.gfan import Gfan
from website.gxdmw.gxdmw import Gxdmw
from website.hexieshe.hexieshe import Hexieshe
from website.huxiu.huxiu import huxiu
from website.ifeng.ifeng import Ifeng
from website.iqiyi.iqiyi import Iqiyi
from website.pk52.pk52 import PK52
from website.qudong.qudong import Qudong
from website.tian52.tian52 import tian52
from website.yesky.yesky import yesky
from website.yeyou.yeyou import YeYou
from website.zdface.zdface import zdface
from website.yzz.yzz import Yzz
from website.zymk.zymk import Zymk
from website.one78.one78 import One78
from website.one7173.one7173 import One7173
from website.u17.u17 import U17
from website.lady8844.lady8844 import Lady8844
from website.narutom.narutom import Narutom
from website.onethreeone.onethreeone import OneThreeOne
from website.tgbus.tgbus import TgBus
from website.sootoo.main import Sootoo
from website.syqnr.syqnr import Syqnr
from website.tianya.tianya import Tianya
from website.toutiao.toutiao import Toutiao
from website.tudou.tudou import Tudou
from website.uuu9.uuu9 import Uuu9
from website.xinhua.xinhua import Xinhua
from website.youku.youku import Youku
from website.zhihu.zhihu import Zhihu
from website.zol.zol import Zol
from website.zongheng.zongheng import ZongHeng
from website.rongshuxia.rongshuxia import RongShuXia
from website.k17.k17 import K17
from website.thepaper.thepaper import Thepaper
from website.yidianzixun.yidianzixun import Yidianzixun
##############################################
from website.sohu.sohu import Sohu
from website.sina.sina import Sina
from website.ishangman.ishangman import ishangman
from website.ithome.main import ithome
from website.jianshu.main import jianshu
from website.jiemian.jiemian import jiemian
from website.jjwxc.jjwxc import Jjwxc
from website.joyme.joyme import Joyme
from website.jrj.main import jrj
from website.kankan.kankan import KanKan
from website.kkk1.kkkManhua import kkkManhua
from website.kr36.kr36 import Kr36
from website.ku6.ku6 import Ku6
from website.kumi.kumi import kumi
from website.laohu.laohu import Laohu
from website.le.le import Le
from website.leiphone.leiphone import Leiphone
from website.maoyan.maoyan import MaoYan
from website.mkzhan.mkzhan import mkzhan
from website.mofang.mofang import Mofang
from website.mtime.mtime import Mtime
from website.muu.muu import muu
from website.one8183.one8183 import One8183
from website.tencent.tencent import Tencent
from website.onesixthree.onesixthree import OneSixThree
from website.onlylady.onlylady import Onlylady
from website.pcauto.pcauto import Pcauto
from website.pcgames.pcgames import Pcgames
from website.poocg.poocg import poocg
from website.pptv.pptv import Pptv
from website.ptbus.ptbus import Ptbus
from website.qidian.qidian import qidian
from website.rayli.rayli import rayli
from website.mop.mop import Mop
from website.hupu.hupu import hupu
from website.gamersky.gamersky import Gamersky
########################################################
# from website.book2200.book import book
# from website.chinabyte.chinabyte import Chinabyte
# from website.chinavalue.chinavalue import Chinavalue
# from website.cine107.cine107 import Cine107
# from website.renren001.renren001 import Renren001
# from website.sfacg.sfacg import Sfacg
# from website.sfw.sfw import Sfw
# from website.dm123.dm123 import Dm123
# from website.dm5.dm5 import Dm5
# from website.sougou.sougou import Sougou
# from website.startup.main import startup
# from website.ea3w.ea3w import Ea3w
# from website.flash8.flash8 import Flash8
# from website.four0407.four0407 import Four0407
# from website.graphmovie.graphmovie import Graphmovie
# from website.hongxiu.hongxiu import HongXiu
# from website.hqcx.main import hqcx
# from website.huanqiu.main import huanqiu
# from website.tadu.tadu import TaDu
# from website.thirtysixKrypton.thirtysixKrypton import ThirtysixKrypton
# from website.wangdafilm.wangdafilm import Wangdafilm
# from website.xie17.xie17 import Xie17
# from website.xxsy.xxsy import Xxsy
# from website.tmtpost.tmtpost import Tmtpost
# from website.zhulang.zhulang import zhulang
# from website.rain8.rain8 import Rain8
################################################################################################################
# @class：SiteFactory
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：主站工厂类
################################################################################################################
class SiteFactory:

    # 全局变量，主站列表
    __sitelist = []

    # 全局变量，初始化标志
    __initialized = False

    # quickmap
    __sitemap = {}

    # no site match list
    __unknowndomainlist = []

    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：初始化内部变量
    ################################################################################################################
    def __init__(self):
        if not SiteFactory.__initialized:
            SiteFactory.__initialized = True

            # SiteFactory.__sitelist.append(AcFun())
            # SiteFactory.__sitelist.append(SevenAcg())
            # SiteFactory.__sitelist.append(Angeeks())
            # SiteFactory.__sitelist.append(Actoys())
            # SiteFactory.__sitelist.append(Adquan())
            # SiteFactory.__sitelist.append(Appgame())
            # SiteFactory.__sitelist.append(Baidu())
            # SiteFactory.__sitelist.append(BaoZou())
            # SiteFactory.__sitelist.append(Bilibili())
            # SiteFactory.__sitelist.append(China())
            # SiteFactory.__sitelist.append(Dm78())
            # SiteFactory.__sitelist.append(Dmzj())
            # SiteFactory.__sitelist.append(domarketing())
            # SiteFactory.__sitelist.append(DoNews())
            # SiteFactory.__sitelist.append(Game3dm())
            # SiteFactory.__sitelist.append(Edugov())
            # SiteFactory.__sitelist.append(Gfan())
            # SiteFactory.__sitelist.append(PK52())
            # SiteFactory.__sitelist.append(Qudong())
            # SiteFactory.__sitelist.append(tian52())
            # SiteFactory.__sitelist.append(yesky())
            # SiteFactory.__sitelist.append(YeYou())
            # SiteFactory.__sitelist.append(zdface())
            # SiteFactory.__sitelist.append(Yzz())
            # SiteFactory.__sitelist.append(Zymk())
            # SiteFactory.__sitelist.append(One78())
            # SiteFactory.__sitelist.append(One7173())
            # SiteFactory.__sitelist.append(U17())
            # SiteFactory.__sitelist.append(Gametanzi())
            # SiteFactory.__sitelist.append(Gxdmw())
            # SiteFactory.__sitelist.append(Lady8844())
            # SiteFactory.__sitelist.append(Narutom())
            # SiteFactory.__sitelist.append(OneThreeOne())
            # SiteFactory.__sitelist.append(TgBus())
            # SiteFactory.__sitelist.append(Cn21())
            # SiteFactory.__sitelist.append(douban())
            # SiteFactory.__sitelist.append(Duowan())
            # SiteFactory.__sitelist.append(Fun())
            # SiteFactory.__sitelist.append(gamelook())
            # SiteFactory.__sitelist.append(Gameres())
            # SiteFactory.__sitelist.append(Hexieshe())
            # SiteFactory.__sitelist.append(huxiu())
            # SiteFactory.__sitelist.append(Gamersky())
            # SiteFactory.__sitelist.append(Ifeng())
            # SiteFactory.__sitelist.append(gao7())
            # SiteFactory.__sitelist.append(Iqiyi())
            # SiteFactory.__sitelist.append(Sootoo())
            # SiteFactory.__sitelist.append(Syqnr())
            # SiteFactory.__sitelist.append(Tianya())
            SiteFactory.__sitelist.append(Toutiao())
            # SiteFactory.__sitelist.append(Tudou())
            # SiteFactory.__sitelist.append(Uuu9())
            # SiteFactory.__sitelist.append(Xinhua())
            # SiteFactory.__sitelist.append(Youku())
            # SiteFactory.__sitelist.append(Zhihu())
            # SiteFactory.__sitelist.append(Zol())
            # SiteFactory.__sitelist.append(ZongHeng())
            # SiteFactory.__sitelist.append(RongShuXia())
            # SiteFactory.__sitelist.append(K17())
            # SiteFactory.__sitelist.append(Thepaper())
            # SiteFactory.__sitelist.append(Yidianzixun())
            ##########################################
            # SiteFactory.__sitelist.append(Sohu())
            # SiteFactory.__sitelist.append(Sina())
            # SiteFactory.__sitelist.append(ishangman())
            # SiteFactory.__sitelist.append(ithome())
            # SiteFactory.__sitelist.append(jianshu())
            # SiteFactory.__sitelist.append(jiemian())
            # SiteFactory.__sitelist.append(Jjwxc())
            # SiteFactory.__sitelist.append(Joyme())
            # SiteFactory.__sitelist.append(jrj())
            # SiteFactory.__sitelist.append(KanKan())
            # SiteFactory.__sitelist.append(kkkManhua())
            # SiteFactory.__sitelist.append(Kr36())
            # SiteFactory.__sitelist.append(Ku6())
            # SiteFactory.__sitelist.append(kumi())
            # SiteFactory.__sitelist.append(Laohu())
            # SiteFactory.__sitelist.append(Le())
            # SiteFactory.__sitelist.append(Leiphone())
            # SiteFactory.__sitelist.append(MaoYan())
            # SiteFactory.__sitelist.append(mkzhan())
            # SiteFactory.__sitelist.append(Mofang())
            # SiteFactory.__sitelist.append(Mtime())
            # SiteFactory.__sitelist.append(muu())
            # SiteFactory.__sitelist.append(Tencent())
            # SiteFactory.__sitelist.append(One8183())
            # SiteFactory.__sitelist.append(OneSixThree())
            # SiteFactory.__sitelist.append(Onlylady())
            # SiteFactory.__sitelist.append(Pcauto())
            # SiteFactory.__sitelist.append(Pcgames())
            # SiteFactory.__sitelist.append(poocg())
            # SiteFactory.__sitelist.append(Pptv())
            # SiteFactory.__sitelist.append(Ptbus())
            # SiteFactory.__sitelist.append(qidian())
            # SiteFactory.__sitelist.append(rayli())
            # SiteFactory.__sitelist.append(Mop())
            # SiteFactory.__sitelist.append(Gamersky())
            # SiteFactory.__sitelist.append(hupu())
            
            ##################################################

            # SiteFactory.__sitelist.append(HongXiu())
            # SiteFactory.__sitelist.append(Graphmovie())
            # SiteFactory.__sitelist.append(hqcx())
            # SiteFactory.__sitelist.append(huanqiu())
            # SiteFactory.__sitelist.append(Huya())
            # SiteFactory.__sitelist.append(book())
            # SiteFactory.__sitelist.append(Chinabyte())
            # SiteFactory.__sitelist.append(Chinavalue())
            # SiteFactory.__sitelist.append(Cine107())
            # SiteFactory.__sitelist.append(Dm123())
            # SiteFactory.__sitelist.append(Dm5())
            # SiteFactory.__sitelist.append(Ea3w())
            # SiteFactory.__sitelist.append(Flash8())
            # SiteFactory.__sitelist.append(Four0407())
            # SiteFactory.__sitelist.append(Renren001())
            # SiteFactory.__sitelist.append(RongShuXia())
            # SiteFactory.__sitelist.append(SeventeenK())
            # SiteFactory.__sitelist.append(Sfacg())
            # SiteFactory.__sitelist.append(Sfw())
            # SiteFactory.__sitelist.append(Sougou())
            # SiteFactory.__sitelist.append(startup())
            # SiteFactory.__sitelist.append(TaDu())
            # SiteFactory.__sitelist.append(Thepaper())
            # SiteFactory.__sitelist.append(ThirtysixKrypton())
            # SiteFactory.__sitelist.append(Tmtpost())
            # SiteFactory.__sitelist.append(Wangdafilm())
            # SiteFactory.__sitelist.append(Xie17())
            # SiteFactory.__sitelist.append(Xxsy())
            # SiteFactory.__sitelist.append(Yidianzixun())
            # SiteFactory.__sitelist.append(zhulang())
            # SiteFactory.__sitelist.append(Rain8())




    ################################################################################################################
    # @functions：getsite
    # @param： URL
    # @return：跟URL匹配的主站
    # @note：根据URL获取主站
    ################################################################################################################
    def getsite(self, url):
        domain = TemplateManager.getdomain(url)
        if domain in SiteFactory.__sitemap:
            for site in SiteFactory.__sitemap[domain]:
                if site.match(url):
                    return site
        if domain in SiteFactory.__unknowndomainlist:
            Logger.getlogging().warning('Site not found for {url}'.format(url=url))
            return WebSite()
        for site in SiteFactory.__sitelist:
            if site.match(url):
                if domain not in SiteFactory.__sitemap:
                    SiteFactory.__sitemap[domain] = []
                SiteFactory.__sitemap[domain].append(site)
                return site
        Logger.getlogging().warning('Site not found for {url}'.format(url=url))
        SiteFactory.__unknowndomainlist.append(domain)
        return WebSite()

    ################################################################################################################
    # @functions：getall
    # @param： none
    # @return：主站列表
    # @note：获取所有的主站
    ################################################################################################################
    def getall(self):
        return SiteFactory.__sitelist