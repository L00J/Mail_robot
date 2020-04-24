#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:22:55
@LastEditTime: 2020-04-24 08:05:35
@Description:
'''
from bin.sendermail import send
from bin.task import run
import imaplib
import configparser
import json
import re
import time
import sys
import imaplib
import sys
from bs4 import BeautifulSoup
from email.parser import Parser


"""
POP3/SMTP协议
接收邮件服务器：pop.exmail.qq.com ，使用SSL，端口号995
接收邮件服务器：imap.exmail.qq.com  ，使用SSL，端口号993
发送邮件服务器：smtp.exmail.qq.com ，使用SSL，端口号465
海外用户可使用以下服务器
接收邮件服务器：hwpop.exmail.qq.com ，使用SSL，端口号995
发送邮件服务器：hwsmtp.exmail.qq.com ，使用SSL，端口号465
"""

config = configparser.ConfigParser()
config.read('my.conf')
config.sections()
mailconf = config['mail']
taskconf = config['task']


class Mail_helper():
    def __init__(self):
        super().__init__()
        self.results = {}
        self.host = mailconf['IMAP_HOST']
        self.email = mailconf['email']
        self.password = mailconf['password']
        self.smtp = mailconf['SMTP_HOST']

    def message(self):
        """
        提取邮件
        """
        server = imaplib.IMAP4_SSL(port='993', host=self.host)
        print('已连接服务器')

        try:
            res = server.login(self.email, self.password)
            print('成功登陆邮箱')
        except Exception as e:
            print("登录失败", e)
            sys.exit(1)

        server.select()
        email_count = len(server.search('ALL')[1][0].split())
        print("待处理邮件: %d" % email_count)

        if email_count > 0:
            typ, email_content = server.fetch(
                f'{email_count}'.encode(), '(RFC822)')
            email_content = email_content[0][1].decode()

            msg = Parser().parsestr(email_content)
            print("邮件类型: %s" % msg.get_content_type())
            self.mail_from = re.findall(r'<(.*?)>', msg['From'])[0]
            print("发件人: %s" % self.mail_from)

            html = msg.get_payload(decode=True)

            soup = BeautifulSoup(html, 'lxml')
            body = soup.find('div').text
            body = body.split()[0]
            print("邮件内容: %s" % body)
            print(mailconf['Bind_Sender'])
            if self.mail_from in mailconf['Bind_Sender']:
                print("这是一封有效的指令! From %s" % self.mail_from)
                print('[+] 发件人:%s' % self.mail_from)

                self.results['sender'] = self.mail_from
                for key in taskconf:
                    if key in body:
                        self.results["task"] = key
                        self.results["code"] = taskconf[key]

            else:
                print("非授信的邮件!")
        else:
            print('没有邮件处理')

        # 根据最新id删除邮件
        server.store(str(email_count), '+FLAGS', '\\Deleted')
        server.expunge()

        server.close
        server.logout
        print("登出邮件系统")

    def exec(self):
        """
        执行任务
        """
        start = time.time()
        html_code = run(self.results['code'])
        self.results['output'] = html_code.replace(
            "\t", "&emsp;&emsp;&emsp;&emsp;").split("\n")
        end = time.time()
        self.results['time'] = "time is %.3fs" % (end-start)

    def feedback(self):
        """
        反馈邮件
        """
        if 'sender' in self.results.keys():
            ret = send(self.mail_from, self.email,
                       self.password, self.smtp, self.results)
            if ret:
                print("邮件发送成功")
            else:
                print("邮件发送失败")
        else:
            print("没有发件人")


if __name__ == '__main__':
    M = Mail_helper()
    while True:

        M.message()
        # print(M.results.keys())
        if "task" in M.results.keys():
            print("执行任务")
            M.exec()
            M.feedback()
        else:
            M.results["task"] = "Null"
            M.results["code"] = "未接收到命令!!!"
            M.feedback()

        print(M.results.items())
        M.results.clear()
        time.sleep(10)
        print("继续监听邮件...")
