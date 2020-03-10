# -*- coding: utf-8 -*-
"""
Author: Eric.zhong
Contact: ericzhong2010@qq.com
Create Time: 2020/03/06
File: CheckRMANLOG.py
Info:  RMAN Backup 日志状态检查并发送告警邮件到指定邮箱
"""
import configparser # 配置文件相关模块
import time
import os
import re
import json
import sys
import requests
import smtplib # 邮件发送相关模块
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
import logging # 日志输出到文件
import traceback # 屏幕错误堆栈格式化

# 多附件处理模块
def send_files(message,files):
    for f in files: # List列表内容拆分处理
        # 读取附件转换为二进制
        attachment = MIMEApplication(open(f, 'rb').read())
        # 从绝对路径将文件名抽取出来
        filename = f.split('\\')
        num = len(filename) - 1
        # 设置邮件头信息，filename是附件名称
        attachment.add_header('Content-Disposition', 'attachment', filename=filename[num])
        message.attach(attachment)

# 邮件发送模块
def send_email(mail_host,mail_port,mail_user,mail_pass,receivers,subject,files,errorlog, message_type='html'):
    # 判断是否有错误日志参数
    if len(errorlog) != 0:
        message = errorlog  # 邮件内容
    else:
        message = subject
    part = MIMEText(message, message_type, 'utf-8')
    message = MIMEMultipart()
    message['From'] = mail_user
    message['To'] = receivers
    # 多收件人分割为List列表
    receivers = receivers.split(',')
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(part)
    # 多附件分割为List列表
    files = files.split(',')
    try:
        if files != []:
            send_files(message,files)
    except:
        pass
    try:
        if mail_port == '465':
            smtpObj = smtplib.SMTP_SSL()
            smtpObj.starttls()
        else:
            smtpObj = smtplib.SMTP()
        try:
            smtpObj.connect(mail_host, mail_port)
        except(smtplib.SMTPHeloError,
               smtplib.SMTPAuthenticationError,
               smtplib.SMTPException
               ) as e:
            logging.error("Error: %s" % e)
        # smtp调试模式
        #smtpObj.set_debuglevel(1)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, receivers,message.as_string())
        logging.info("邮件发送成功:"+subject)
        print("邮件发送成功:"+subject)
        return True
    except smtplib.SMTPException as e:
        logging.info("Failure to send email: %s" % str(e))
        return False

# 企业微信发送模块
def Send_Messge(corpid,corpsecret,touser,text):
    # 通过传入的参数拼接请求链接
    Get_Access_Token_Url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+corpid+"&corpsecret="+corpsecret
    # 通过请求链接获取access_token
    access_token=json.loads(requests.get(Get_Access_Token_Url).text)['access_token']
    # 接口地址拼接
    Put_Url="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token
    # 拼接发送内容及格式
    data={'touser': touser, 'msgtype': 'text', 'agentid': 1000002, 'text': {'content': text}, 'safe': 0}
    Response_Code=requests.post(Put_Url,json.dumps(data))
    # 通过返回码判断命令是否执行成功，成功返回0，不成功返回1
    if Response_Code.status_code==200:
        logging.info("企业微信发送成功！")
        return 0
    else:
        logging.error("企业微信发送失败！")
        return 1

def main():
    # 判断备份状态与邮件操作
    try:
        isExistError = 0
        errorlog = ""
        with open(filepath) as f:
            for lines in f.readlines():
                # 多关键字切分为List列表并循环判断
                kwlist = keyword.split(',')
                for kw in kwlist:
                    # re.findall()方法查找关键字是否包含在读入的行数据中
                    if len(re.findall(kw, lines)) != 0:
                        # 如果存在错误日志，变量数量增加
                        isExistError += 1
                        # 记录错误日志信息
                        errorlog = errorlog + lines + "<br/>"
        # 判断是否存在错误日志
        if isExistError == 0:
            subject = "[{0}] RMANBackup备份成功！".format(customername)
        else:
            subject = "[{0}] RMANBackup备份失败！".format(customername)
    except FileNotFoundError:
        subject = "[{0}] RMANBackup备份失败，请检查是否正常执行备份任务！".format(customername)
        errorlog = "日志路径不存在 {0} 文件".format(filepath)
    # 判断是否发送微信信息
    if wechatstatus != 0:
        Send_Messge(corpid, corpsecret, touser, subject)
    # 判断是否发送邮件信息
    if emailstatus != 0:
        send_email(mail_host, mail_port, mail_user, mail_pass, receivers, subject, filepath, errorlog)

if __name__ == '__main__':
    # 日志参数值
    logging.basicConfig(filename='CheckRMANLOG.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    # 读取参数值
    conf = configparser.ConfigParser()
    # utf-8-sig读取可以避免notepad编辑引起的"\ufeff"隐藏字符
    conf.read('config.ini', "utf-8-sig")
    if conf.has_section('Global') != True:
        logging.error("config.ini配置文件丢失，请检查配置。")
        sys.exit()
    # 日志检查相关
    customername = conf['Global']['CustomerName']
    logpath = conf['Global']['LOGPath']
    logprefix = conf['Global']['LOGPrefix']
    logext = conf['Global']['LOGExt']
    keyword = conf['Global']['Keyword']
    # 检查日志路径拼接
    filepath = os.path.abspath(os.path.join(logpath, logprefix+time.strftime("%Y%m%d", time.localtime())+logext))
    # 企业微信参数值
    wechatstatus= int(conf['Wechat']['wechatstatus'])
    corpid = conf['Wechat']['corpid']
    corpsecret = conf['Wechat']['corpsecret']
    touser = conf['Wechat']['touser']
    # 邮件服务参数值
    emailstatus= int(conf['Email']['emailstatus'])
    mail_host = conf['Email']['mail_host']
    mail_port = int(conf['Email']['mail_port'])
    mail_user = conf['Email']['mail_from']
    mail_pass = conf['Email']['mail_pass']
    receivers = conf['Email']['receivers']

    try:
        main()
    except:
        s = traceback.format_exc()
        logging.error(s)

