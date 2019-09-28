#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: plate_perspective.py
@time: 2019-09-04 13:26
"""
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils')
from email_ops import send_email
import html_ops

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

stock = '山鹰纸业'

stock_series = pd.read_pickle(os.path.join(PROJ_DIR, 'finance/data/stock_dict.pkl'))
fund_otc_series = pd.read_pickle(os.path.join(PROJ_DIR, 'finance/data/fund_otc_series.pkl'))
mongo = PyMongoWrapper()
time_range = 'near_1_year'
start_date = datetime.now() - timedelta(days=365*5)


# 基本面 area、industry、sw_industry、市值、市值排名
table = mongo.getCollection('finance', 'stock_basic')
df_base = mongo.findAll(table, {'ts_code': stock_series.loc[stock]}, fieldlist=['name', 'area', 'industry', 'market'],
                   returnFmt='df')
# print(df)
table = mongo.getCollection('finance', 'swclass')
dft = mongo.findAll(table, {'股票代码': stock_series.loc[stock].map(lambda s: s.split('.')[0]).tolist()},
                   fieldlist=['股票名称', '行业名称'],
                   returnFmt='df')
dft.columns = ['name', 'swclass']
df_base = pd.merge(df_base, dft, on='name')


table = mongo.getCollection('finance', 'stock_daily_basic1')
dft = mongo.findAll(table, {'$and': [{'trade_date': '20190926'}, {'ts_code': stock_series.loc[stock]}]},
                   fieldlist=['ts_code', '市盈率（总市值/净利润）', '市净率（总市值/净资产）', '总市值', '流通市值（万元）', 'rank'],
                   returnFmt='df')

df_base = pd.merge(df_base, dft, on='name')
df_base.set_index('name', inplace=True)
df_base = df_base.T.reset_index()
print()

# 行情
# 基准
table = mongo.getCollection('finance', '000001.SH')
df = mongo.findAll(table, {'trade_date': {'$gte': start_date}}, fieldlist=['trade_date', 'pct_chg'],
                    sort=[('trade_date', 1)], returnFmt='df')
for i in dfr.itertuples():
    # 下载股票行情
    cmd = f"python {PROJ_DIR}/finance/stock2mongo.py --ts_code {i.ts_code}"
    r = os.system(cmd)
    table = mongo.getCollection('finance', i.ts_code)

    dft = mongo.findAll(table, {'trade_date': {'$gte': start_date}}, fieldlist=['trade_date', 'pct_chg'], returnFmt='df')
    df = pd.merge(df, dft, on='trade_date', how='left')

df = df.fillna(0)
df = df.set_index('trade_date')
for i in range(df.shape[1]):
    df.iloc[:, i] = (1+df.iloc[:, i]/100).cumprod()
df.columns = ['000001.SH'] + dfr.name.tolist()
# print(df.shape)
# print(df.head())
# print(df.tail())

# 计算近n日涨幅

# print(df1y)
# 近1周涨幅
df1w = pd.DataFrame(((df.iloc[-1] / df.iloc[-6]) - 1).sort_values(ascending=False))
# print(df1w)
# df1w.reset_index(inplace=True)

# 近1月涨幅
df1m = pd.DataFrame(((df.iloc[-1] / df.iloc[-21]) - 1).sort_values(ascending=False))
# 近3月涨幅
df3m = pd.DataFrame(((df.iloc[-1] / df.iloc[-63]) - 1).sort_values(ascending=False))
# 近6月涨幅
df6m = pd.DataFrame(((df.iloc[-1] / df.iloc[-126]) - 1).sort_values(ascending=False))
# 近1年涨幅排序
df1y = pd.DataFrame((df.iloc[-1]-1))
df_mean = pd.DataFrame(df.mean()-1)
df_std = pd.DataFrame(df.std())
df1w = pd.concat([df1w, df1m, df3m, df1y, df_mean, df_std], axis=1, sort=True)
df1w.columns = ['1周涨幅', '1月涨幅', '3月涨幅', '1年涨幅', '平均涨幅', 'std']
df1w = df1w.applymap(lambda e: round(e, 2))
df1w = df1w.T
df1w = df1w.reset_index()

print(df1w)
# df1w['index_1m'] = df1m.index.tolist()
# df1w['涨幅_1m'] = list(map(lambda v: round(v, 2), df1m.iloc[:, 0].values.tolist()))
# df1w['index_3m'] = df3m.index.tolist()
# df1w['涨幅_3m'] = list(map(lambda v: round(v, 2), df3m.iloc[:, 0].values.tolist()))
# df1w['index_6m'] = df6m.index.tolist()
# df1w['涨幅_6m'] = list(map(lambda v: round(v, 2), df6m.iloc[:, 0].values.tolist()))
# df1w['index_1y'] = df1y.index.tolist()
# df1w['涨幅_1y'] = list(map(lambda v: round(v, 2), df1y.iloc[:, 0].values.tolist()))
# print(df1w)
d = html_ops.create_html(f'report报告')
t1 = html_ops.create_label('h2', f'基本面')
d('body').append(t1)
table = html_ops.create_table(df_base)
d('body').append(table)
t1 = html_ops.create_label('h2', f'行情')
d('body').append(t1)
table = html_ops.create_table(df1w)
d('body').append(table)
d('body').append('<br>')

# 绘制近n日走势图
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
df.plot(title='近1年涨幅', figsize=(14, 6))
img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'a.png')
plt.savefig(img_path)
img = html_ops.create_img(img_path)
d('body').append(img)
d('body').append('<br>')
# plt.show()
df3m = df.iloc[-63:]/df.iloc[-63]
df3m.plot(title='近3月涨幅', figsize=(14, 6))
plt.savefig(img_path)
img = html_ops.create_img(img_path)
d('body').append(img)
d('body').append('<br>')


html_ops.output2html(d, 'tmp.html')