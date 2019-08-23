#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: cal_portfolio_val.py
@time: 2019-08-22 15:33

计算每日投资组合的价值
"""
import os
import sys
sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# print(sys.path)
from config import LOG_PATH, portfolio
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/finance')
from stock_wrapper import df2dicts_stock, daily
import argparse
from datetime import datetime, timedelta
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/config')
from logging_utils import get_logger
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils')
from email_ops import send_email
import html_ops
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

log_path = os.path.join(LOG_PATH, 'output.log')
logger = get_logger(__file__, file_handler=True, log_path=log_path)


if __name__ == '__main__':

    mongo = PyMongoWrapper()
    # 获取基金的值
    rlist = []
    total_val = fund_val = stock_val = 0
    for i in portfolio['fund']:
        table = mongo.getCollection('finance', i[0])
        r = list(mongo.findAll(table, fieldlist=['trade_date', 'close'], sort=[('trade_date', -1)], limit=1))[0]
        rlist.append((i[0], r['close'], i[1], r['trade_date']))
        fund_val += r['close'] * i[1]
    stock_series = pd.read_pickle('finance/data/stock_dict.pkl')
    for i in portfolio['stock']:
        table = mongo.getCollection('finance', stock_series.loc[i[0]])
        r = list(mongo.findAll(table, fieldlist=['trade_date', 'close'], sort=[('trade_date', -1)], limit=1))[0]
        rlist.append((i[0], r['close'], i[1], r['trade_date']))
        stock_val += r['close'] * i[1]
    logger.info(rlist)
    total_val = fund_val + stock_val
    logger.info(f'total_val: {total_val}, fund_val: {fund_val}, stock_val: {stock_val}')
    # 图片
    labels = [i[0] for i in rlist]
    students = [i[1]*i[2] for i in rlist]
    plt.pie(students, labels=labels, autopct='%3.2f%%', startangle=45, shadow=True,
            )
    # 设置x，y轴刻度一致，这样饼图才能是圆的
    plt.axis('equal')
    plt.title('百分比')
    img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp', 'a.png')
    plt.savefig(img_path)
    subject = 'portfolio_val'
    # 构造文字内容
    rr = '\n'.join([f'{i[0]} {i[1]} {i[2]} {str(i[3])[:10]}' for i in rlist])
    logger.info(rr)
    text = f'total_val1: {total_val}, fund_val: {fund_val}, stock_val: {stock_val}'
    d = html_ops.create_html('report报告222')

    d('body').append('<p>Hello world222!</p><br>')
    d('body').append('Here is the <a href="http://www.baidu.com">link</a> you wanted.<br>')
    table = html_ops.create_table(['code', 'close', 'vol', 'trade_date'], rlist)
    d('body').append(table)
    d('body').append('<br>')
    d('body').append(f'{text}<br>')
    img = html_ops.create_img(img_path)
    d('body').append(img)

    send_email(subject, text, d.outer_html())
