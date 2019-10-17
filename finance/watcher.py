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
stock_dict = {
    '厦门钨业': 'sh600549',
    '西安银行': 'sh600928',
    '航天发展': 'sz000547',
    '中兴通讯': 'sz000063',
    '首钢股份': 'sz000959',
    '金证股份': 'sh600446',
    '山鹰纸业': 'sh600567',
    '东方航空': 'sh600115',
    '中信证券': 'sh600030',
    '亨通光电': 'sh600487',
}

targets=[
    ('中兴通讯', 31.8, 'lte'),
    ('首钢股份', 3.42, 'lte'),
    # ('航天发展', 10.46, 'lte'),
    ('金证股份', 21.14, 'lte'),
    ('西安银行', 7.2, 'lte'),
    ('亨通光电', 15.54, 'lte'),
    # ('厦门钨业', 13.32, 'lte'),
]

url = 'http://hq.sinajs.cn/list='

for t in targets:
    url += stock_dict[t[0]] + ','

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
    send_email('watcher', str(rs))