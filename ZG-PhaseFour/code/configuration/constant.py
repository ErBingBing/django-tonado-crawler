# coding=utf-8
################################################################################################################
# @file: constant.py
# @author: Sun Xinghua
# @date:  2016/11/21 9:44
# @version: Ver0.0.0.100
# @note:
################################################################################################################

from utility import const

# 存储路径
const.SPIDER_STORAGE_DOMAIN = 'storage'
# 生成的临时文件根目录
const.SPIDER_TEMPLATE_WORK_DIRECTORY = 'spider.template.work.directory'
# done文件临时存放路径
const.SPIDER_DONE_TEMP_PATH = 'done'
# done文件转换为json文件生成路径
const.SPIDER_JSON_TEMP_PATH = 'json'
# ETL数据路径
const.SPIDER_OUTPUT_TEMP_PATH = 'output'
# 临时URL生成路径
const.SPIDER_URLS_TEMP_PATH = 'urls'
# S2 Query信息输入路径
const.SPIDER_QUERY_TEMP_PATH = 'query'
const.SPIDER_TIEBA_TEMP_PATH = 'tieba'
const.SPIDER_WAIBU_TEMP_PATH = 'waibu'
# Imageurl临时生成路径
const.SPIDER_IMAGEURL_TEMP_PATH = 'imageurl'
# S1 URL输入文件
const.SPIDER_S1_INPUT_FILE = 'spider.s1.url.file'
# S2 Query信息输入文件
const.SPIDER_S2_INPUT_FILE = 'spider.s2.query.file'
# S3 QueryUrl信息输入文件
const.SPIDER_S3_INPUT_FILE = 'spider.s3.query.file'
## S4 waibuQuerys
#const.SPIDER_S4_INPUT_FILE = 'spider.s4.query.file'
# 最终结果输出路径
const.SPIDER_OUTPUT_PATH = 'spider.output.path'
# URL Backup
const.SPIDER_URL_BACKUP_PATH = 'spider.url.backup.path'
# Data Backup
const.SPIDER_DATA_BACKUP_PATH = 'spider.data.backup.path'
# PUC Backup
const.SPIDER_WAIBU_BACKUP_PATH = 'spider.waibu.backup.path'
# url error
const.SPIDER_URL_RESULT_ERROR_FILE = 'spider.url.result.error.file'
# S2 URL
const.SPIDER_S2_QUERY_URLS_FILE = 'spider.s2.query.urls.file'
# 统计
const.SPIDER_INFO_REPORT_FILE = 'spider.info.report.file'
# spider.output.path.limit
const.SPIDER_OUTPUT_PATH_LIMIT = 'spider.output.path.limit'
# output file format
const.SPIDER_OUTPUT_FILENAME_SUFFIX = 'spider.output.filename.suffix'

# databaase
const.SPIDER_DATABASE_DOMAIN = 'database'
const.SPIDER_DATABASE_IP = 'spider.database.ip'
const.SPIDER_DATABASE_PORT = 'spider.database.port'
const.SPIDER_DATABASE_USERNAME = 'spider.database.usename'
const.SPIDER_DATABASE_PASSWORD = 'spider.database.password'
const.SPIDER_DATABASE_DATABASE = 'spider.database.database'
const.SPIDER_DATABASE_CHARSET = 'spider.database.charset'
#mysql的导出文件的工具
const.SPIDER_DATABASE_EXPORT_TOOLS = 'spider.database.export.tools'


# 异常处理
const.SPIDER_EXCEPTION_DOMAIN = 'exception'
# 超时
const.SPIDER_WAIT_PLATFORM_TIMEOUT = 'spider.wait.platform.timeout'
# 最多循环次数
const.SPIDER_RECYCLE_MAX_TIMES = 'spider.recycle.max.times'
# 周期
const.SPIDER_WAITING_PERIOD = 'spider.wait.period'
# 数据有效期
const.SPIDER_VALID_PERIOD = 'spider.valid.period'
# update max retry times
const.SPIDER_UPLOAD_RETRY_TIMES = 'spider.upload.retry.times'
# success threshold
const.SPIDER_FAILED_THRESHOLD = 'spider.failed.threshold'
# exception report
const.SPIDER_REPORT_EXCEPTION_TOOL = 'spider.report.exception.tool'
# s1 max comment pages
const.SPIDER_S1_MAX_COMMENT_PAGES = 'spider.s1.max.comment.pages'
# s2 max comment pages
const.SPIDER_S2_MAX_QUERY_PAGES = 'spider.s2.max.query.pages'

# 下载平台相关配置
const.SPIDER_TENCENT_PLATFORM_DOMAIN = 'platform'
#是否是从服务器
const.SPIDER_TENCENT_PLATFORM_SLAVE = 'spider.tencent.platform.master'
#外部数据
const.SPIDER_TENCENT_PLATFORM_WAIBU = 'spider.tencent.platform.waibu'
#  下载集群机器ip列表
const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST = 'spider.tencent.platform.machine.list'
const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST_WAIBU = 'spider.tencent.platform.machine.list.waibu'
const.SPIDER_TENCENT_PLATFORM_MACHINE_LIST_TIEBA = 'spider.tencent.platform.machine.list.tieba'
# 上传下载平台URL
const.SPIDER_TENCENT_PLATFORM_UPLOAD_URL = 'spider.tencent.platform.upload.url'
# 转换工具
const.SPIDER_TENCENT_PLATFORM_PARSE_TOOL = 'spider.tencent.platform.parse.tool'
const.SPIDER_TENCENT_PLATFORM_PARSE_TOOL_IMG = 'spider.tencent.platform.parse.tool.img'
# 下载平台输出路径
const.SPIDER_TENCENT_PLATFORM_OUTPUT_PATH = 'spider.tencent.platform.output.path'
# 下载平台Task列表
const.SPIDER_TENCENT_PLATFORM_TASK_LIST = 'spider.tencent.platform.task.list'
# 下载平台Webkit Task列表
const.SPIDER_TENCENT_PLATFORM_WEBKIT_TASK_LIST = 'spider.tencent.platform.webkit.task.list'
# 调度Task列表
const.SPIDER_SCHEDULER_LIST = 'spider.scheduler.list'
# 外部数据api列表
const.SPIDER_TENCENT_PLATFORM_WBTASK_LIST = 'spider.tencent.platform.wbtask.list'
# slave path
const.SPIDER_PUSH_PATH = 'spider.push.path'
# push path
const.SPIDER_PUSH_PATH_MASTER = 'spider.push.path.master'


# 调度程序相关配置
const.SPIDER_SCHEDULER_DOMAIN = 'scheduler'
const.SCHEDULER_URL_PATH = 'scheduler.url.path'
const.SCHEDULER_DONE_PATH = 'scheduler.done.path'
# POST下载程序相关配置
const.SPIDER_LOCAL_DOMAIN = 'downloader'
# Post下载列表
const.SPIDER_LOCAL_DOWNLOADER_LIST = 'spider.local.downloader.list'
const.SPIDER_LOCAL_WHOAMI = 'downloader.whoami'
const.DOWNLOADER_URL_BACKUP = 'downloader.url.backup'
const.DOWNLOADER_INTERVAL = 'downloader.interval'

# Log相关配置
const.SPIDER_LOGGING_DOMAIN = 'logging'

# 配置文件存储位置
const.SPIDER_LOG_CONFIGURE_FILE = 'spider.log.configure.file'

# 数据库相关配置
const.SPIDER_DB_DOMAIN = 'db'
# 数据库存储位置
const.SPIDER_DB_FILEPATH = 'spider.db.filepath'

# S2相关配置
const.SPIDER_S2_DOMAIN = 's2'
# S2元搜有效天数
const.SPIDER_QUERY_LAST_DAYS = 'spider.query.last.days'

SPIDER_TASKID = '.task.id'
SPIDER_TASKNAME = '.task.name'
SPIDER_USERID = '.user.id'
DOWNLOADER_IP = '.ip'
DOWNLOADER_PORT = '.port'
DOWNLOADER_USERNAME = '.username'
DOWNLOADER_PASSWORD = '.password'
DOWNLOADER_URL_PATH = '.url.path'
DOWNLOADER_DONE_PATH = '.done.path'
#外部数据信息
SPIDER_WBTASK_NAME = '.task.name'
SPIDER_WBTASK_TOKEN = '.task.token'
SPIDER_WBTASK_APPID = '.task.appid'


# 渠道：201(S1: url)，202（S2: query）
SPIDER_CHANNEL = 'channel'
SPIDER_CHANNEL_S1 = '201'
SPIDER_CHANNEL_S2 = '202'
SPIDER_CHANNEL_S3 = '203'
# S2特有字段：新闻(301)，视频(302)，贴吧(303)
SPIDER_S2_WEBSITE_TYPE = 'type'
SPIDER_S2_WEBSITE_NEWS = '301'
SPIDER_S2_WEBSITE_VIDEO = '302'
SPIDER_S2_WEBSITE_TIEBA = '303'

#
SPIDER_S2_WEBSITE_QUERY = 'query'

# 字符编码类型
# 字符编码GBK
CHARSET_GBK = 'gbk'
# 字符编码GB2312
CHARSET_GB2312 = 'gb2312'
# 字符编码UTF8
CHARSET_UTF8 = 'utf-8'
# 默认编码
CHARSET_DEFAULT = CHARSET_UTF8

ORIGINALTIME = '1970-01-01 08:00:00'
# GZIP压缩文件头
GZIP_CODE = u'%1F%8B%08'
# 非图片内容的html文件头
HTML_SUFIX = '%3C!DOC'
# debug off
DEBUG_FLAG_OFF = 0
# windows debug flag
DEBUG_FLAG_WINDOWS = 1
# linux(virtual) debug flag
DEBUG_FLAG_LINUX = 2

# 调试标识
DEBUG_FLAG = 1

#ERRORCODE
ERRORCODE_FAIL_LOAD_OTHERS    =	10000
ERRORCODE_FAIL_LOAD_UP	      = 11000
ERRORCODE_FAIL_LOAD_DOWN      = 12000
ERRORCODE_SITE_NOGET_SITE     = 20000
ERRORCODE_SITE_NOGET_TEMPLATE = 20001
ERRORCODE_SITE_NOGET_XPATHVALUE= 30000
ERRORCODE_SITE_NOGET_CMTNUM   = 30001
ERRORCODE_SITE_NOGET_CLICKNUM = 30002
ERRORCODE_SITE_NOGET_COMMNETS = 30003
ERRORCODE_EXCEPTTION_OTHERS   = 40000
ERRORCODE_EXCEPTTION_NET      = 40001
ERRORCODE_EXCEPTTION_JSON     = 40002
ERRORCODE_WARNNING_OTHERS     = 50000
ERRORCODE_WARNNING_NOMATCHTITLE= 50001
ERRORCODE_WARNNING_NOMATCHTIME = 50002
ERRORCODE_WARNNING_OUTTIME     = 50003
ERRORCODE_WARNNING_NORESULTS   = 50004

ERRORINFO={
    ERRORCODE_FAIL_LOAD_OTHERS:   u'上传或下载失败;下载失败后超时重试等。',
    ERRORCODE_FAIL_LOAD_UP:       u'上传失败。',
    ERRORCODE_FAIL_LOAD_DOWN:     u'下载失败。',
    ERRORCODE_SITE_NOGET_SITE:    u'不在给定的网站-主站范围内.',
    ERRORCODE_SITE_NOGET_TEMPLATE:u'不在网站-子站范围内,可能模板template配置错误。',
    ERRORCODE_SITE_NOGET_XPATHVALUE:u'某个字段没有取到值；或配置的模板的xpath错误。',
    ERRORCODE_SITE_NOGET_CMTNUM:  u'没有取到评论量，或获取评论量失败。',
    ERRORCODE_SITE_NOGET_CLICKNUM:u'没有取到播放量，或获取播放量失败。',
    ERRORCODE_SITE_NOGET_COMMNETS:u'获取评论异常时，没有获取到评论。',
    ERRORCODE_EXCEPTTION_OTHERS:  u'其他异常。',
    ERRORCODE_EXCEPTTION_NET:    u'网络异常。',
    ERRORCODE_EXCEPTTION_JSON:   u'api获取josn内容异常；或api拼接错误，或下载异常导致。',
    ERRORCODE_WARNNING_OTHERS:   u'其他警告。',
    ERRORCODE_WARNNING_NOMATCHTITLE:u'标题匹配错误。',
    ERRORCODE_WARNNING_NOMATCHTIME: u'发布时间在指定周期外。',
    ERRORCODE_WARNNING_OUTTIME:     u'超时警告。',
    ERRORCODE_WARNNING_NORESULTS: '该页面没有您要的搜索结果'
    }


# 下载模式
REMOTE_DOWNLOADER_MIN_LINES = 200

# 输出URL编码
URL_ENCODE_FLAG = False

# WEBKIT SUFFIX
WEBKIT_FILE_SUFFIX = '_WKT'
# POST SUFFIX
POST_FILE_SUFFIX   = '_POST'
# IMG SUFFIX
IMG_FILE_SUFFIX    = '_IMG'

# REQUEST TYPE
REQUEST_TYPE_COMMON = 0
REQUEST_TYPE_WEBKIT = 1
REQUEST_TYPE_POST = 2
REQUEST_TYPE_IMG = 3
# spider run timeout (hour)
SPIDER_RUN_TIMEOUT_HOUR = '23:00'

# retry times of push file
SPIDER_PUSHFILE_RETRY_TIMES = 5
SPIDER_MAX_CELL_LENGTH = 300*1024
SPIDER_S1_MAX_LINE_PER_FILE = 2000

#baidutieba pattern constant, neizhan or quanzhan
TIEBA_URL_PATTERN1 = 'http[s]{0,1}://tieba\.baidu\.com/f\?.*kw\=(.*\w+)&.*'
TIEBA_URL_PATTERN12 = 'http[s]{0,1}://tieba\.baidu\.com/f\?.*kw\=(.*\w+)'
TIEBA_URL_PATTERN2 = 'http[s]{0,1}://tieba\.baidu\.com/f/search/res\?.*qw\=(.*)&.*'
TIEBA_URL_PATTERN22 = 'http[s]{0,1}://tieba\.baidu\.com/f/search/res\?.*qw\=(.*)'


#仅抽取指定站点的url
DEBUG_SITEPATTERNS = []



