#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:22:55
@LastEditTime: 2020-04-19 23:38:46
@Description: 
'''

from bin.task import run
from bin.monitor import grab_message
import configparser


config = configparser.ConfigParser()
config.read('my.conf')
config.sections()
mailconf = config['mail']
taskconf = config['task']
popHost = mailconf['POP3_HOST']
email = mailconf['email']
password = mailconf['password']


if __name__ == '__main__':
    task = grab_message(popHost, email, password)
    command = task[0].strip()
    print(command)
    if command in taskconf:
        run(taskconf[command])
    else:
        print('[-] ERROR [%s] 是未定义的参数！！！' % command)
