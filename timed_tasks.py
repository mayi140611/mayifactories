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
from read_config_file import read_config_file
params = read_config_file('/Users/luoyonggui/PycharmProjects/mayifactories/config.txt')


logger = logging.getLogger(__file__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(os.path.join(params['LOG_PATH'], 'output.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('111This is a log info')
logger.debug('Debugging')
logger.warning('Warning exists')
logger.info('Finish')

stock2mongo.py [-h] [--ts_code TS_CODE] [--mode MODE]
                      [--start_date START_DATE] [--end_date END_DATE]

