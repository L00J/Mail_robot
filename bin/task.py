#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-19 21:26:03
@LastEditTime: 2020-04-22 14:27:32
@Description:
'''
import os
import subprocess


def run(command):
    print("[+] [%s] 任务执行中 ..." % command)
    output = subprocess.Popen(command, stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE, shell=True).stdout.read().decode("GBK")

    # res = subprocess.run(command, shell=True)
    # # res = os.system(command)
    print(output)
    return output


if __name__ == '__main__':
    res = run('ifconfig')
