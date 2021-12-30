import argparse
import os
import logging
import configparser
import signal

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def pwd() -> str:
	return os.getcwd()


def Exit(signum, frame):
	exit()


class Config:
	UserName = ""
	PassWord = ""
	FilePath = ""
	FtpServerLogPath = ""
	IP = ""
	PORT = ""

	def __init__(self, config: str):
		Parser = configparser.ConfigParser()
		if os.access(config, os.F_OK) == False:
			print("Error Can't find ini config")
			exit()

		Parser.read(config)
		Parser.sections()

		self.IP = Parser["BaseConfig"]["ServerIpAddr"]
		self.PORT = Parser["BaseConfig"]["ServerPort"]
		self.FilePath = Parser["BaseConfig"]["ServerRoot"]
		self.FtpServerLogPath = Parser["BaseConfig"]["FtpServerLog"]
		self.UserName = Parser["UserConfig"]["UserName"]
		self.PassWord = Parser["UserConfig"]["UserPassword"]


def FtpServer(config: Config):
	authorizer = DummyAuthorizer()
	authorizer.add_user(config.UserName, config.PassWord, config.FilePath, perm='elradfmwMT')
	authorizer.add_anonymous(os.getcwd())

	handler = FTPHandler
	handler.authorizer = authorizer
	logging.basicConfig(filename=config.FtpServerLogPath, level=logging.INFO)
	handler.banner = "Windows Simple Ftp Server Connected -- author HongDaYu"

	# 将 port str 转化为 int 类型的ip地址
	address = (config.IP, int(config.PORT))
	server = FTPServer(address, handler)
	server.max_cons = 256  # 服务器的最大连接数量
	server.max_cons_per_ip = 5  # 最多可以链接的ip数量
	server.serve_forever()  # 只有一个ftp 端口


if __name__ == '__main__':
	signal.signal(signal.SIGINT, Exit)  # 如果退出程序就马上退出,使系统回收程序的系统资源
	# 默认情况下 是获取当前路径下的配置文件,当然也可以指定路径
	cmd = argparse.ArgumentParser(description="Ftp Server Command Config")
	# 如果不可以可以使用默认的配置路径
	cmd.add_argument('-f', type=str, default=pwd(), help="指定Ftp 服务器的配置文件")
	print("Please don't quit this console,if you want to use Ftp Server")
	# 使用当前的工作目录
	args = cmd.parse_args()
	args.f += "\\FtpServer.ini"
	print(args.f)
	config = Config(args.f)
	FtpServer(config)