#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: stock_daily_basic2mongo.py
@time: 2019-08-28 11:24
"""
import os
import sys
sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import LOG_PATH
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/finance')
from stock_wrapper import get_tushare_pro
import argparse
from datetime import datetime, timedelta
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/config')
from logging_utils import get_logger

log_path = os.path.join(LOG_PATH, 'output.log')
logger = get_logger(__file__, file_handler=True, log_path=log_path)

mongo = PyMongoWrapper()
dbname = 'finance'
table_name = 'stock_daily_basic1'
table = mongo.getCollection(dbname, table_name)
if not mongo.isExists(dbname, table_name):
    mongo.setUniqueIndex(dbname, table_name, ['ts_code', 'trade_date'])
pro = get_tushare_pro()
f = 'ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,total_share,float_share,free_share,total_mv,circ_mv'
# df = pro.daily_basic(ts_code='', trade_date=datetime.now().strftime('%Y%m%d'), fields=f)
df = pro.daily_basic(ts_code='', trade_date='20190926', fields=f)
# df = pro.daily_basic(ts_code='', trade_date='20190827', fields=f)
if not df.empty:
    logger.info(f'请求到{len(df)}条数据！')
    df.columns = [
        'ts_code',
         'trade_date',
         'close',
         '换手率（%）',
         '换手率（自由流通股）',
         '量比',
         '市盈率（总市值/净利润）',
         '市盈率（TTM）',
         '市净率（总市值/净资产）',
         '市销率',
         '市销率（TTM）',
         '总股本',
         '流通股本',
         '自由流通股本',
         '总市值',
         '流通市值（万元）'
    ]
    df = df.sort_values('总市值', ascending=False)
    df['rank'] = range(1, df.shape[0]+1)
    print(df.head())
    try:
        mongo.insertDataframe(df, dbname, table_name)
        logger.info(f'存入mongodb complete!')
    except Exception as e:
        logger.warning(str(e))
else:
    logger.warning(f'请求数据为空！')