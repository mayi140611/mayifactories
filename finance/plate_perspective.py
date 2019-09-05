#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: plate_perspective.py
@time: 2019-09-04 13:26
"""
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper

# plate = '银行'
# plate = '证券'
plate = '白酒'
time_range = 'near_1_year'
start_date = datetime.now() - timedelta(days=365)
stock_series = pd.read_pickle('finance/data/stock_dict.pkl')
fund_otc_series = pd.read_pickle('finance/data/fund_otc_series.pkl')
mongo = PyMongoWrapper()
# 获取该板块的所有股票
table = mongo.getCollection('finance', 'stock_basic')
dfr = mongo.findAll(table, {'industry': plate}, returnFmt='df')
print(dfr.shape)
print(dfr.head())
# 下载股票行情

# 从mongo中load相应的close, pct_chg
# 基准
table = mongo.getCollection('finance', '000001.SH')
df = mongo.findAll(table, {'trade_date': {'$gte': start_date}}, fieldlist=['trade_date', 'pct_chg'],
                    sort=[('trade_date', 1)], returnFmt='df')
for i in dfr.itertuples():
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
df1w.reset_index(inplace=True)
df1w.columns = ['index_1w', '涨幅_1w']
# 近1月涨幅
df1m = pd.DataFrame(((df.iloc[-1] / df.iloc[-21]) - 1).sort_values(ascending=False))
# 近3月涨幅
df3m = pd.DataFrame(((df.iloc[-1] / df.iloc[-63]) - 1).sort_values(ascending=False))
# 近6月涨幅
df6m = pd.DataFrame(((df.iloc[-1] / df.iloc[-126]) - 1).sort_values(ascending=False))
# 近1年涨幅排序
df1y = pd.DataFrame((df.iloc[-1]-1).sort_values(ascending=False))
df1w['index_1m'] = df1m.index.tolist()
df1w['涨幅_1m'] = df1m.iloc[:, 0].values.tolist()
df1w['index_3m'] = df3m.index.tolist()
df1w['涨幅_3m'] = df3m.iloc[:, 0].values.tolist()
df1w['index_6m'] = df6m.index.tolist()
df1w['涨幅_6m'] = df6m.iloc[:, 0].values.tolist()
df1w['index_1y'] = df1y.index.tolist()
df1w['涨幅_1y'] = df1y.iloc[:, 0].values.tolist()
print(df1w)

# 绘制近n日走势图
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
df.plot()
plt.show()
df3m = df.iloc[-63:]/df.iloc[-63]
df3m.plot()
plt.show()

