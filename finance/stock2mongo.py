#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: stock2mongo.py
@time: 2019-08-11 23:01
"""
import os
import sys
sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import LOG_PATH
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/finance')
from stock_wrapper import daily
import argparse
from datetime import datetime, timedelta
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/config')
from logging_utils import get_logger

log_path = os.path.join(LOG_PATH, 'output.log')
logger = get_logger(__file__, file_handler=True, log_path=log_path)

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_stocks_to_mongo(stocks, mode='stock'):
    import pandas as pd
    stock_series = pd.read_pickle(os.path.join(PROJ_DIR, 'finance/data/stock_dict.pkl'))
    mongo = PyMongoWrapper()
    db = mongo.getDb('finance')
    tables = db.list_collection_names()
    start_date = '20010101'
    end_date = datetime.now().strftime('%Y%m%d')
    for name in stocks:
        if mode == 'stock':
            ts_code = stock_series.loc[name]

        table = mongo.getCollection('finance', ts_code)
        if ts_code not in tables:
            logger.info(f'{ts_code}表在数据库中不存在，新建表插入！')

            if mode in ['stock', 'index', 'fund', 'otc_fund']:
                mongo.setUniqueIndex('finance', ts_code, ['trade_date'])
        else:
            logger.info(f'{ts_code}表在数据库中存在，update表数据！')
            if mode in ['stock', 'index', 'fund']:
                r = mongo.findAll(table, fieldlist=['trade_date'], sort=[('trade_date', -1)], limit=1)
                r = list(r)
                if len(r) > 0:
                    d = r[0]['trade_date']
                    start_date = (d + timedelta(days=1)).strftime('%Y%m%d')
        try:
            if mode in ['stock', 'index', 'fund']:
                df = daily(ts_code, start_date=start_date, end_date=end_date, mode=mode)
            elif mode in ['otc_fund']:
                import requests
                import json
                import pandas as pd
                from pyquery import PyQuery as pq
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.1.6000',
                }
                dd = dict()
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
                print(df)
                # print(d, dd, df)

            logger.info(f'共请求到{df.shape[0]}条数据！')
            if df.shape[0] > 0:
                mongo.insertDataframe(df, 'finance', ts_code, df_index='trade_date')
            else:
                logger.warning('请求数据为空！')
        except Exception as e:
            logger.error(str(e))
        mongo.close()


if __name__ == '__main__':
    mongo = PyMongoWrapper()
    table = mongo.getCollection('finance', 'stock_basic')
    df = mongo.findAll(table, fieldlist=['name'], returnFmt='df')
    STOCK_NAMES = df.name.tolist()[::-1]
    get_stocks_to_mongo(STOCK_NAMES)

