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
# sys.path.append(os.path.abspath('.'))
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
import pandas as pd

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

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # email
    smtpserver = 'smtp.163.com'
    username = '13585581243@163.com'
    password = 'Lyg140611'  # 授权码
    sender = '13585581243@163.com'
    # 收件人为多个收件人
    receiver = ['13585581243@163.com']

    subject = 'portfolio_val'
    # 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'ian@163.com <ian@163.com>'
    # 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
    msg['To'] = ";".join(receiver)
    msg['Date']='2019-08-16'

    # 构造文字内容
    text = f'total_val: {total_val}, fund_val: {fund_val}, stock_val: {stock_val}'
    text_plain = MIMEText(text, 'plain', 'utf-8')
    msg.attach(text_plain)
    # 发送邮件
    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com')
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
