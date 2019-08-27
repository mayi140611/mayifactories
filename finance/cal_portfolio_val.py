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
    rlist = []
    stock_series = pd.read_pickle('finance/data/stock_dict.pkl')
    for t in ['fund', 'stock', 'otc_fund']:
        for i in portfolio[t]:
            tname = i[0] if t == 'fund' else stock_series.loc[i[0]]
            table = mongo.getCollection('finance', tname)
            r = list(mongo.findAll(table, fieldlist=['trade_date', 'close', 'pct_chg'], sort=[('trade_date', -1)], limit=1))[0]
            rlist.append((i[0], r['close'], i[1], r['pct_chg'], t, r['trade_date']))

    df = pd.DataFrame(rlist, columns=['code', 'close', 'vol', '涨幅', '类型', 'trade_date'])
    df['市值'] = df['close'] * df['vol']
    df['change'] = ((df['close'] - df['close']/(1+df['涨幅']/100)) * df['vol']).map(int)

    def t(i):
        return f'<font color="red">{i}</font>' if i > 0 else f'<font color="green">{i}</font>'
    df['trade_date'] = df['trade_date'].dt.date
    df['市值'] = df['市值'].map(int)
    df['涨幅'] = df['涨幅'].map(t)
    df.sort_values('市值', ascending=False, inplace=True)
    logger.info(rlist)
    total_val = df['市值'].sum()
    loss = df['change'].sum()
    logger.info(f'total_val: {total_val}, loss: {loss}')
    # 图片
    labels = df['code']
    val = df['市值']
    plt.pie(val, labels=labels, autopct='%3.2f%%', startangle=45, shadow=True,
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
    text = f'total_val1: {total_val}, loss: {loss}'
    d = html_ops.create_html('report报告222')

    d('body').append('<p>Hello Ian!</p><br>')
    d('body').append('Here is the <a href="http://www.baidu.com">link</a> you wanted.<br>')
    table = html_ops.create_table(df[['code', '涨幅', 'change', '市值', 'close', 'vol', '类型', 'trade_date']])
    d('body').append(table)
    d('body').append('<br>')
    d('body').append(f'{text}<br>')
    img = html_ops.create_img(img_path)
    d('body').append(img)
    # html_ops.output2html(d, 'tmp.html')
    send_email(subject, text, d.outer_html())
