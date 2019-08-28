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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
    parser.add_argument('--ts_code', type=str, help='train data source')
    parser.add_argument('--mode', type=str, default='stock', help='#stock|index|fund|otc_fund, 默认stock')
    parser.add_argument('--start_date', type=str, default='20010101', help='#默认读取股票')
    parser.add_argument('--end_date', type=str, default=datetime.now().strftime('%Y%m%d'), help='#默认读取股票')
    args = parser.parse_args()
    logger.info(args)

    mongo = PyMongoWrapper()
    db = mongo.getDb('finance')
    tables = db.list_collection_names()
    table = mongo.getCollection('finance', args.ts_code)
    if args.ts_code not in tables:
        logger.info(f'{args.ts_code}表在数据库中不存在，新建表插入！')

        if args.mode in ['stock', 'index', 'fund', 'otc_fund']:
            mongo.setUniqueIndex('finance', args.ts_code, 'trade_date')
    else:
        logger.info(f'{args.ts_code}表在数据库中存在，update表数据！')
        if args.mode in ['stock', 'index', 'fund']:
            r = mongo.findAll(table, fieldlist=['trade_date'], sort=[('trade_date', -1)], limit=1)
            d = list(r)[0]['trade_date']
            args.start_date = (d + timedelta(days=1)).strftime('%Y%m%d')
    try:
        if args.mode in ['stock', 'index', 'fund']:
            df = daily(args.ts_code, start_date=args.start_date, end_date=args.end_date, mode=args.mode)
        elif args.mode in ['otc_fund']:
            import requests
            import json
            import pandas as pd
            from pyquery import PyQuery as pq
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.1.6000',
            }
            r = requests.get(f'http://fundgz.1234567.com.cn/js/{args.ts_code}.js', headers=headers)
            s = r.text
            d = json.loads(s[s.find('{'):(s.find('}') + 1)])
            dd = dict()
            dd['trade_date'] = datetime.strptime(d['jzrq'], '%Y-%m-%d')
            dd['close'] = float(d['dwjz'])
            r = requests.get(f'http://fund.eastmoney.com/{args.ts_code}.html')
            r.encoding = 'utf8'
            root = pq(r.text)
            d1 = root(
                '#body > div:nth-child(12) > div > div > div.fundDetail-main > div.fundInfoItem > div.dataOfFund > dl.dataItem02 > dd.dataNums > span.ui-font-middle.ui-num')
            dd['pct_chg'] = float(d1.text()[:-1])
            df = pd.DataFrame(columns=['trade_date', 'close', 'pct_chg'])
            df = df.append(dd, ignore_index=True)
            df.set_index('trade_date', inplace=True)
            print(df)
            # print(d, dd, df)

        logger.info(f'共请求到{df.shape[0]}条数据！')
        if df.shape[0] > 0:
            mongo.insertDataframe(df, 'finance', args.ts_code, df_index='trade_date')
        else:
            logger.warning('请求数据为空！')
    except Exception as e:
        logger.error(str(e))