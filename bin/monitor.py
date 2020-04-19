#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:25:38
@LastEditTime: 2020-04-19 23:36:55
@Description:
'''


from email.header import decode_header
from email.parser import Parser
import poplib
import re


def decode_str(s):
    l = decode_header(s)
    value, charset = l[0]
    if charset:
        value = value.decode(charset)

    if len(l) == 2:
        value_tmp = l[1][0]
        value = value + value_tmp.decode(charset)
    return value


def get_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get("Content-type", "").lower()
        pos = content_type.find("charset=")
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def print_msg(msg, indent=0):
    if indent == 0:
        for header in ["From", "To", "Subject", "Date"]:
            value = msg[header]
            if value:
                value = decode_str(value)
            print("%s%s: %s" % (" " * indent, header, value))

    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print("%spart %s" % (" " * indent, n))
            print_msg(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain" or content_type == "text/html":
            content = msg.get_payload(decode=True)
            charset = get_charset(msg)
            if charset:
                content = content.decode(charset)
            return ("%sText: %s" % (" " * indent, content))
        else:
            print("%sAttachment: %s" % (" " * indent, content_type))


def grab_message(popHost, email, password):
    server = poplib.POP3(popHost, 110)
    print(server.getwelcome())  # 打印POP3服务器的欢迎文字

    server.user(email)
    server.pass_(password)
    print('Message: %s条. Size: %s' % server.stat())  # stat()返回邮件数量和占用空间:
    # 获得某一封邮件的内容
    resp, mails, octets = server.list()  # 返回邮件数量和每个邮件的大小
    index = len(mails)  # 获得最后一封的索引
    resp, lines, octets = server.retr(index)    # 返回由参数标识的邮件的全部文本
    # print(lines)

    # 解读处理
    msg_content = b"\r\n".join(lines).decode("utf-8")  # byte字符串
    msg = Parser().parsestr(msg_content)    # 解析为普通字符串
    message = print_msg(msg)
    # print(message)

    task = re.findall(r'task:(.*?)[<>]', message)  # 提取body内容
    # 通过configparser匹配

    return task
