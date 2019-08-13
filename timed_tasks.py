#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: timed_tasks.py
@time: 2019-08-08 21:20

定时任务
"""
import logging
import os
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/config')
from config import LOG_PATH, TS_CODES

logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(os.path.join(LOG_PATH, 'output.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# logger.info('111This is a log info')
# logger.debug('Debugging')
# logger.warning('Warning exists')
# logger.info('Finish')

"""
读取数据，存入MongoDB
stock2mongo.py [-h] [--ts_code TS_CODE] [--mode MODE]
                      [--start_date START_DATE] [--end_date END_DATE]
"""
for TS_CODE in TS_CODES:
    logger.info(f'读取数据{TS_CODE}，存入MongoDB')
    cmd = f"python finance/stock2mongo.py --ts_code {TS_CODE}"
    r = os.system(cmd)
    if r == 0:
        logger.info(f'读取数据{TS_CODE}，存入MongoDB，complete')
    else:
        logger.error(f'读取数据{TS_CODE}，存入MongoDB，failure')
