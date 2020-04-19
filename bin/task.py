#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:26:03
@LastEditTime: 2020-04-19 23:41:59
@Description: 
'''
import os


def run(command):
    print("[+] [%s] 任务执行中 ..." % command)
    os.system(command)


if __name__ == '__main__':
    run('xxx')
