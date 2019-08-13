#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: stock2mongo.py
@time: 2019-08-11 23:01
"""
import os
from config import LOG_PATH
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/finance')
from stock_wrapper import df2dicts_stock, daily
import argparse
from datetime import datetime
import logging
logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(os.path.join(LOG_PATH, 'output.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
    parser.add_argument('--ts_code', type=str, help='train data source')
    parser.add_argument('--mode', type=str, default='stock', help='#默认读取股票')
    parser.add_argument('--start_date', type=str, default='20010101', help='#默认读取股票')
    parser.add_argument('--end_date', type=str, default=datetime.now().strftime('%Y%m%d'), help='#默认读取股票')
    args = parser.parse_args()
    logger.info(args.ts_code)
    df = daily(args.ts_code, start_date=args.start_date, end_date=args.end_date, mode=args.mode)
    if df.shape[0] > 0:
        mongo = PyMongoWrapper()

        table = mongo.getCollection('finance', args.ts_code)
        if args.mode == 'stock':
            mongo.setUniqueIndex('finance', args.ts_code, 'trade_date')

        table.insert_many(df2dicts_stock(df))
    else:
        logger.warning('请求数据为空！')