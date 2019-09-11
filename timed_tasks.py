#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: timed_tasks.py
@time: 2019-08-08 21:20

定时任务
"""
import pandas as pd
import os

from config import LOG_PATH, STOCK_NAMES, FUND_NAMES, INDEX_NAMES, OTC_FUND_NAMES
import sys
# print(sys.path)
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/config')
from logging_utils import get_logger
log_path = os.path.join(LOG_PATH, 'output.log')
logger = get_logger(__file__, file_handler=True, log_path=log_path)

"""
读取数据，存入MongoDB
stock2mongo.py [-h] [--ts_code TS_CODE] [--mode MODE]
                      [--start_date START_DATE] [--end_date END_DATE]
"""
stock_series = pd.read_pickle('finance/data/stock_dict.pkl')
for name in STOCK_NAMES:
    logger.info(f'读取数据{name}，存入MongoDB')
    cmd = f"python finance/stock2mongo.py --ts_code {stock_series.loc[name]}"
    r = os.system(cmd)
    if r == 0:
        logger.info(f'读取数据{name}，存入MongoDB，complete')
    else:
        logger.error(f'读取数据{name}，存入MongoDB，failure')
for name in FUND_NAMES:
    logger.info(f'读取数据{name}，存入MongoDB')
    cmd = f"python finance/stock2mongo.py --ts_code {name} --mode fund"
    r = os.system(cmd)
    if r == 0:
        logger.info(f'读取数据{name}，存入MongoDB，complete')
    else:
        logger.error(f'读取数据{name}，存入MongoDB，failure')
for name in INDEX_NAMES:
    logger.info(f'读取数据{name}，存入MongoDB')
    cmd = f"python finance/stock2mongo.py --ts_code {name} --mode index"
    r = os.system(cmd)
    if r == 0:
        logger.info(f'读取数据{name}，存入MongoDB，complete')
    else:
        logger.error(f'读取数据{name}，存入MongoDB，failure')
fund_otc_series = pd.read_pickle('finance/data/fund_otc_series.pkl')
for name in OTC_FUND_NAMES:
    logger.info(f'读取数据{name}，存入MongoDB')
    cmd = f"python finance/stock2mongo.py --ts_code {fund_otc_series.loc[name]} --mode otc_fund"
    r = os.system(cmd)
    if r == 0:
        logger.info(f'读取数据{name}，存入MongoDB，complete')
    else:
        logger.error(f'读取数据{name}，存入MongoDB，failure')
