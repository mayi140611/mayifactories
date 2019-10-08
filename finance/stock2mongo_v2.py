#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: stock2mongo_v2.py
@time: 2019-10-01 22:03
"""
import os
PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/finance')
from tushare_wrapper import TushareWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
mongo = PyMongoWrapper()
ts = TushareWrapper()
# 查询当前所有正常上市交易的股票列表
# df = ts.get_stocks_info()
# print(df.head())
# mongo.insertDataframe(df, 'finance_n', 'stocks_info')

# 获取股票历史数据
# start_date = '20110101'
# end_date = datetime.now().strftime('%Y%m%d')
# db_name = 'finance_n'
# tb_name = 'stocks_daily'
# table = mongo.getCollection(db_name, tb_name)
# mongo.setUniqueIndex(db_name, tb_name, ['trade_date', 'ts_code'])
# count = 3611
# import time
# for ts_code in df.ts_code.tolist()[count:]:
#     data = ts.daily(ts_code, start_date, end_date, mode='stock')
#     print(f'{count}, {ts_code}: {data.shape}')
#     mongo.insertDataframe(data, db_name, tb_name, df_index='trade_date')
#     count += 1
#     time.sleep(0.004)
#     # break

# 获取stock_daily_basic
# df = ts.get_daily_basic('20190930')
# print(df.head())
# tb_name = 'stock_daily_basic'
# table = mongo.getCollection(db_name, tb_name)
# # mongo.setUniqueIndex(db_name, tb_name, ['trade_date', 'ts_code'])
# if not df.empty:
#     mongo.insertDataframe(df, db_name, tb_name)


# # 获取场内fund历史数据
# start_date = '20110101'
# end_date = datetime.now().strftime('%Y%m%d')
# db_name = 'finance_n'
# tb_name = 'stocks_daily'
# table = mongo.getCollection(db_name, tb_name)
# FUND_NAMES = [
#     '510300.SH',
#     '510500.SH',
#     '512800.SH',
#     '512880.SH',
#     '512660.SH',
#     '518880.SH',
#     '512580.SH',
#     '513050.SH',
#     '159938.SZ',
#     '159915.SZ',
#     '159920.SZ',
# ]
# count = 0
#
# import time
# for ts_code in FUND_NAMES[count:]:
#     data = ts.daily(ts_code, start_date, end_date, mode='fund')
#     print(f'{count}, {ts_code}: {data.shape}')
#     mongo.insertDataframe(data, db_name, tb_name, df_index='trade_date')
#     count += 1

# 获取场内otc_fund历史数据
OTC_FUND_NAMES = [
    '易方达证券公司分级',
    '广发纯债债券A',
    '兴全可转债混合',
    '博时信用债纯债债券A',
    '广发中债7-10年国开债指数A',
    '华夏中证500ETF联接A',
    '富国中证红利指数增强',
    '广发医药卫生联接A',
    '华夏上证50ETF联接A',
    '建信中证500指数增强A',
    '广发养老指数A',
    '华宝标普油气上游股票',
    '广发创业板ETF联接A',
    '长信可转债债券A',
    '易方达安心回报债券A',
    '广发中证500ETF联接C',
    '广发中证全指金融地产联接A',
    '富国中证500指数(LOF)',
    '广发中证环保ETF联接A',
    '富国沪深300指数增强',
    '广发中证传媒ETF联接A',
    '华安德国30(DAX)联接',
]

import requests
import json
import pandas as pd
from pyquery import PyQuery as pq
fund_otc_series = pd.read_pickle(os.path.join(PROJ_DIR, 'finance/data/fund_otc_series.pkl'))
db_name = 'finance_n'
tb_name = 'stocks_daily'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.1.6000',
}
for name in OTC_FUND_NAMES:
    dd = dict()
    ts_code = fund_otc_series.loc[name]
    r = requests.get(f'http://fund.eastmoney.com/{ts_code}.html')
    r.encoding = 'utf8'
    root = pq(r.text)
    d1 = root(
        '#body > div:nth-child(12) > div > div > div.fundDetail-main > div.fundInfoItem > div.dataOfFund > dl.dataItem02 > dd.dataNums > span.ui-font-middle.ui-num')
    dd['pct_chg'] = float(d1.text()[:-1])
    d1 = root(
        '#body > div:nth-child(12) > div > div > div.fundDetail-main > div.fundInfoItem > div.dataOfFund > dl.dataItem02 > dd.dataNums > span.ui-font-large.ui-num')
    dd['close'] = float(d1.text())
    d1 = root(
        '#body > div:nth-child(12) > div > div > div.fundDetail-main > div.fundInfoItem > div.dataOfFund > dl.dataItem02 > dt > p'
    )
    dd['trade_date'] = datetime.strptime(d1.text()[-11:-1], '%Y-%m-%d')
    df = pd.DataFrame(columns=['trade_date', 'close', 'pct_chg'])
    df = df.append(dd, ignore_index=True)
    df.set_index('trade_date', inplace=True)
    df['ts_code'] = ts_code
    print(df)
    if df.shape[0] > 0:
        mongo.insertDataframe(df, db_name, tb_name, df_index='trade_date')
