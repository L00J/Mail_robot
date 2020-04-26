#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:22:55
@LastEditTime: 2020-04-25 22:26:28
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
        self.imap_server = mailconf['IMAP_HOST']
        self.email = mailconf['email']
        self.password = mailconf['password']
        self.smtp = mailconf['SMTP_HOST']

    def message(self):
        """
        提取邮件
        """
        print("[+]信任的邮箱:%s" % mailconf['Bind_Mail'])
        server = imaplib.IMAP4_SSL(port='993', host=self.imap_server)
        print('[+]已连接服务器')

        try:
            res = server.login(self.email, self.password)
            print('[+]成功登陆邮箱')
        except Exception as e:
            print("[-]登录邮箱失败", e)
            sys.exit(1)

        server.select()
        email_count = len(server.search('ALL')[1][0].split())

        if email_count > 0:
            print("[+]待处理邮件: %d" % email_count)
            typ, email_content = server.fetch(
                f'{email_count}'.encode(), '(RFC822)')
            email_content = email_content[0][1].decode()
            # 经过parsestr处理过后生成一个字典
            msg = Parser().parsestr(email_content)
            html = msg.get_payload(decode=True)
            soup = BeautifulSoup(html, 'lxml')
            body = soup.find('div').text
            body = body.split()[0]
            print("邮件类型: %s" % msg.get_content_type())
            print("邮件内容: %s" % body)

            re_from = re.findall(r'<(.*?)>', msg['From'])[0]
            self.results["re_From"] = re_from
            print("发件人: %s" % re_from)
            if re_from in mailconf['Bind_Mail']:
                self.results["From"] = msg["From"].split()
                if msg["Cc"]:
                    re_Cc = re.findall(
                        r'<(.*?)>', msg['Cc'])[0]
                    self.results["re_Cc"] = re_Cc
                    self.results["Cc"] = msg["Cc"].split()
                    print("抄送邮件: %s" % re_Cc)

                self.results['Bind_Mail'] = re_from
                print("Bind_Mail: %s" % self.results['Bind_Mail'])
                for key in taskconf:
                    if key in body:
                        self.results["task"] = key
                        self.results["code"] = taskconf[key]

                    # 根据最新id删除邮件
                    server.store(str(email_count), '+FLAGS', '\\Deleted')
                    server.expunge()

                else:
                    print("[-]待处理邮件: %d" % email_count)
                    print("[-]非授信的邮件!")
        else:
            print('[-]没有邮件处理 ~')

        server.close
        server.logout
        print("[+]登出邮件系统 ~")

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
        # 判断邮箱是否受到信任
        if 'Bind_Mail' in self.results.keys():
            ret = send(self.smtp, self.email, self.password, self.results)
            if ret:
                print("[+]邮件发送成功")
            else:
                print("[-]邮件发送失败")

        else:
            print("[-]不发送邮件 ~")


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
        for num in range(10, 0, -1):
            time.sleep(1)
            print(num)

        print("[+]继续监听邮件...")
