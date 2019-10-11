#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: watcher.py
@time: 2019-10-09 08:03
"""
import requests
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils')
from email_ops import send_email


targets=[
    ('sz000063', 31.77, 'lte'),
    ('sz000547', 10.46, 'lte'),
    ('sh600446', 21, 'lte'),
    ('sh600928', 7.2, 'lte'),
]

url = 'http://hq.sinajs.cn/list='

for t in targets:
    url += t[0] + ','

r = requests.get(url)
# print(r.text)

rs = r.text.split(';\n')
rr = []
for r in rs:
    if r:
        s = r.find('"')
        r1 = r[s + 1: -2].split(',')
        rr.append([r1[0], r1[3]])
    # print(r1)
# print(rr)
rs = []
for i in range(len(targets)):
    if float(rr[i][1]) <= targets[i][1]:
        rs.append(rr[i])

if rs:
    send_email('watcher', str(rr))