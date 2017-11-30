# encoding=utf-8
import os

import paramiko


################################################################################################################
# @class：SSHConnection
# @author：Sun Xinghua
# @date：
# @note：
################################################################################################################
from log.spiderlog import Logger
from utility.fileutil import FileUtility


class SSHConnection(object):
    ################################################################################################################
    # @functions：__init__
    # @param： none
    # @return：none
    # @note：SSHConnection初始化内部变量
    ################################################################################################################
    def __init__(self, host, port, username, pwd):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd

    ################################################################################################################
    # @functions：connect
    # @param： none
    # @return：none
    # @note：SSH连接
    ################################################################################################################
    def connect(self):
        try:
            t = paramiko.Transport((self.host, self.port))
            t.connect(username=self.username, password=self.pwd)
            self.__transport = t
        except Exception, e:
            Logger.getlogging().error('ssh连接失败{Exception}:{error}'.format(Exception=Exception, error=e))
            return False
        return True
    ################################################################################################################
    # @functions：close
    # @param： none
    # @return：none
    # @note：SSH关闭
    ################################################################################################################
    def close(self):
        self.__transport.close()

    ################################################################################################################
    # @functions：upload
    # @param： none
    # @return：none
    # @note：上传文件
    ################################################################################################################
    def upload(self, localFilePath, targetFilePath):
        # 连接，上传
        # file_name = self.create_file()
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 将本地文件上传至服务器
        sftp.put(localFilePath, targetFilePath)

    ################################################################################################################
    # @functions：download
    # @param： none
    # @return：none
    # @note：下载文件
    ################################################################################################################
    def download(self, targetFilePath, localFilePath):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        sftp.get(targetFilePath, localFilePath)

    ################################################################################################################
    # @functions：ls
    # @param： none
    # @return：none
    # @note：遍历路径下文件
    ################################################################################################################
    def ls(self, host, port, username, pwd, lsPath):
        list = []
        # 实例化SSHClient
        client = paramiko.SSHClient()
        # 自动添加策略，保存服务器的主机名和密钥信息
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接SSH服务端，以用户名和密码进行认证
        try:
            client.connect(host, port, username=username, password=pwd)
        except Exception, e:
            Logger.getlogging().error('ssh连接失败{Exception}:{error}'.format(Exception=Exception, error=e))
            return list
        # 打开一个Channel并执行命令
        stdin, stdout, stderr = client.exec_command('cd ' + lsPath + ';ls')
        # 打印执行结果
        list = stdout.readlines()
        # 关闭SSHClient
        client.close()
        return list

    ################################################################################################################
    # @functions：rename
    # @param： none
    # @return：none
    # @note：修改文件名
    ################################################################################################################
    def rename(self, host, port, username, pwd, before, after):
        # 实例化SSHClient
        client = paramiko.SSHClient()
        # 自动添加策略，保存服务器的主机名和密钥信息
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接SSH服务端，以用户名和密码进行认证
        try:
            client.connect(host, port, username=username, password=pwd)
            # 打开一个Channel并执行命令
            client.exec_command('mv ' + before + ' ' + after)
        except Exception, e:
            Logger.getlogging().error('ssh连接失败{Exception}:{error}'.format(Exception=Exception, error=e))



################################################################################################################
# @functions：sshupload
# @param： none
# @return：none
# @note：上传
################################################################################################################
def sshupload(host, port, username, pwd, targetPath, localFilePath):
    ssh = SSHConnection(host, port, username, pwd)
    if ssh.connect():
        length = len(localFilePath.split('/'))
        fileName = localFilePath.split('/')[length - 1]
        ssh.upload(localFilePath, targetPath + fileName + 'tmp')
        ssh.close()
        ssh.rename(host, port, username, pwd, targetPath + fileName + 'tmp', targetPath + fileName)
        return True
    else:
        return False

################################################################################################################
# @functions：sshdownload
# @param： none
# @return：none
# @note：下载
################################################################################################################
def sshdownload(host, port, username, pwd, targetFilePath, localPath):
    Logger.getlogging().info('scp -P {port} {username}@{host}:{file} {path}'.format(port=port, username=username, host=host, file=targetFilePath, path=localPath))
    ssh = SSHConnection(host, port, username, pwd)
    if ssh.connect():
        length = len(targetFilePath.split('/'))
        fileName = targetFilePath.split('/')[length - 1]
        ssh.download(targetFilePath, localPath + fileName + '.tmp')
        ssh.close()
        FileUtility.move(localPath + fileName + '.tmp', localPath + fileName)
        return True
    else:
        return False

################################################################################################################
# @functions：sshls
# @param： none
# @return：文件list
# @note：遍历
################################################################################################################
def sshls(host, port, username, pwd, lsPath):
    ssh = SSHConnection(host, port, username, pwd)
    list = ssh.ls(host, port, username, pwd, lsPath)
    return list


if __name__ == '__main__':
    os.chdir('..')
    host = '121.42.202.116'
    port = 22
    username = 'root'
    pwd = 'Huashu123#'
    lsPath = '/tmp'
    targetFilePath = '/tmp/5'
    localPath = 'E:/work/data/temp/'
    targetPath = '/tmp/'
    localFilePath = 'E:/work/data/temp/7'
    # sshls(host, port, username, pwd, lsPath)
    # sshdownload(host, port, username, pwd, targetFilePath, localPath)
    sshupload(host, port, username, pwd, targetPath, localFilePath)
