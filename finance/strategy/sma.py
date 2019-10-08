#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: SMA.py
@time: 2019-10-01 03:56

Fast Moving Average: 短期移动均线，因为窗口越小，均线对价格的灵敏度越高，改变越fast
本质：趋势交易，利用均线的迟滞降低扰动
优点：降低扰动，可以过滤掉噪音，从而显著降低交易频率
主要缺点：
1、由于均线的迟滞，会错过初期的那部分涨幅。
但这是趋势交易不可以避免的结果，否则就是逆势抄底了。。。
2、股票走势一般呈现一种缓涨急跌的走势，这时均线的迟滞就会造成大的回撤
改进措施：
可以通过仓位管理来降低回撤：
如买入时，全仓买入。
等到股价第一次回踩fast_ma时short 1/3的仓位
等到股价第二次回踩fast_ma时short 1/3的仓位
然后装死，直到fast_ma下穿slow_ma时清仓

这里有一些细节，如可以预判，股价即将上穿时 就买入半仓，等到完全上穿后买入剩下的半仓，
没有如期上穿，就择时清仓
卖出时也可以预判，当fast_ma即将下穿slow_ma清仓

买入时点的选择：尽量在14点以后，


改进：
    增加交易手续费
    开盘价买入
    控制回撤
    仓位管理
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import ffn
import matplotlib.pyplot as plt
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper


class SMA:
    @classmethod
    def get_stocks_dict(cls):
        mongo = PyMongoWrapper()
        table = mongo.getCollection('finance_n', 'stocks_info')
        df = mongo.findAll(table, fieldlist=['ts_code', 'name'], returnFmt='df')
        stock_names = df.name.tolist()
        stock_ts_codes = df.ts_code.tolist()

        return dict(zip(stock_names, stock_ts_codes)), dict(zip(stock_ts_codes, stock_names))

    @classmethod
    def get_stocks_dict_top_n(cls, n, t_date):
        mongo = PyMongoWrapper()
        table = mongo.getCollection('finance_n', 'stock_daily_basic')
        df = mongo.findAll(table, {'trade_date': pd.to_datetime(t_date)}, fieldlist=['ts_code'],
                           sort=[('rank', 1)], limit=n, returnFmt='df')
        stock_reverse_dict = cls.get_stocks_dict()[1]

        return df.ts_code.map(lambda c: stock_reverse_dict[c]).tolist()

    @classmethod
    def get_hist(cls, name=None, ts_code=None, count=365):
        if not ts_code:
            stocks_dict = cls.get_stocks_dict()[0]
            ts_code = stocks_dict[name]
        # start_date = datetime.now() - timedelta(days=count)
        mongo = PyMongoWrapper()
        table = mongo.getCollection('finance_n', 'stocks_daily')
        # df = mongo.findAll(table, {'trade_date': {'$gte': start_date}},
        #                    fieldlist=['trade_date', 'pct_chg'], returnFmt='df')
        df = mongo.findAll(table, {'ts_code': ts_code}, fieldlist=['trade_date', 'pct_chg'],
                           sort=[('trade_date', -1)], limit=count, returnFmt='df')
        df.set_index('trade_date', inplace=True)
        df.sort_index(inplace=True)
        df['net'] = (1 + df['pct_chg'] / 100).cumprod()
        del df['pct_chg']
        # print(df.head())
        # print(df.tail())
        return df

    @classmethod
    def sma_base(cls, name=None, ts_code=None, count=365, fast_ma=8, slow_ma=60):
        """

        """
        df = cls.get_hist(name, ts_code, count)

        symbol = 'net'
        data = df

        data['fast_ma'] = data[symbol].rolling(fast_ma).mean()
        data['slow_ma'] = data[symbol].rolling(slow_ma).mean()
        data.dropna(inplace=True)

        data['position'] = np.where(data['fast_ma'] > data['slow_ma'], 1, 0)
        data['position'] = data['position'].shift(1)  # 因为当天的收益是拿不到的，
        data.plot(secondary_y='position', figsize=(14, 6))
        plt.show()
        data['returns'] = np.log(data[symbol] / data[symbol].shift(1))

        data['strat'] = data['position'] * data['returns']

        data.dropna(inplace=True)
        data['hold_earnings'] = data[['returns']].cumsum().apply(np.exp)
        data['strat_earnings'] = data[['strat']].cumsum().apply(np.exp)
        ax = data[['hold_earnings', 'strat_earnings']].plot(figsize=(14, 6))
        data['position'].plot(ax=ax, secondary_y='position', style='--', figsize=(14, 6))
        plt.show()
        print(np.exp(data[['returns', 'strat']].sum()))
        print(data[['returns','strat']].std())
        # 计算最大回撤

        hold_max_drawdown = ffn.calc_max_drawdown(data.hold_earnings)
        strat_max_drawdown = ffn.calc_max_drawdown(data.strat_earnings)
        print(f'hold_max_drawdown: {hold_max_drawdown}')
        print(f'strat_max_drawdown: {strat_max_drawdown}')

    @classmethod
    def sma_v1(cls, name=None, ts_code=None, count=365, fast_ma=8):
        """
        当股价大于fast_ma时买入，低于时卖出
        """
        df = cls.get_hist(name, ts_code, count)

        symbol = 'net'
        data = df

        data['fast_ma'] = data[symbol].rolling(fast_ma).mean()
        data.dropna(inplace=True)

        data['position'] = np.where(data.net > data['fast_ma'], 1, 0)
        data['position'] = data['position'].shift(1)  # 因为当天的收益是拿不到的，
        data.plot(secondary_y='position', figsize=(14, 6))
        plt.show()
        data['returns'] = np.log(data[symbol] / data[symbol].shift(1))

        data['strat'] = data['position'] * data['returns']

        data.dropna(inplace=True)
        data['hold_earnings'] = data[['returns']].cumsum().apply(np.exp)
        data['strat_earnings'] = data[['strat']].cumsum().apply(np.exp)
        ax = data[['hold_earnings', 'strat_earnings']].plot(figsize=(14, 6))
        data['position'].plot(ax=ax, secondary_y='position', style='--', figsize=(14, 6))
        plt.show()
        print(np.exp(data[['returns', 'strat']].sum()))
        print(data[['returns','strat']].std())
        # 计算最大回撤

        hold_max_drawdown = ffn.calc_max_drawdown(data.hold_earnings)
        strat_max_drawdown = ffn.calc_max_drawdown(data.strat_earnings)
        print(f'hold_max_drawdown: {hold_max_drawdown}')
        print(f'strat_max_drawdown: {strat_max_drawdown}')

    @classmethod
    def stock_select(cls, name=None, ts_code=None, fast_ma=8, slow_ma=60):
        data = cls.get_hist(name, ts_code, slow_ma)
        symbol = 'net'
        # data['fast_ma'] = data[symbol].rolling(fast_ma).mean()
        data['slow_ma'] = data[symbol].rolling(slow_ma).mean()
        print(data.tail())
        return all([
            # data.iloc[-1].fast_ma < data.iloc[-1].slow_ma,
            abs(data.iloc[-1].slow_ma - data.iloc[-1].net) < (data.iloc[-1].net * 0.01),
            # (data.iloc[-1].slow_ma - data.iloc[-1].fast_ma) < abs(data.iloc[-1].net * 0.01),
            # data.iloc[-1].fast_ma < data.iloc[-2].fast_ma,  # 短期均线保持向下走势
            # data.iloc[-1].net > data.iloc[-1].slow_ma,
            # data.iloc[-1].fast_ma > data.iloc[-2].fast_ma,  # 短期均线保持向上走势
            # data.iloc[-1].slow_ma > data.iloc[-2].slow_ma,  # 长期均线保持向上走势
        ])

    @classmethod
    def stocks_select(cls, names='all', fast_ma=8, slow_ma=60):
        if names=='all':
            names = cls.get_stocks_dict()[0].keys()
        rs = []
        print(datetime.now())
        print(f'股票池容量：{len(names)}')
        count = 0
        # import multiprocessing
        # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        for name in names:
            print(f'{count}, {name}')
            count += 1

            try:
                if cls.stock_select(name, fast_ma=fast_ma, slow_ma=slow_ma):
                    rs.append(name)
            except Exception as e:
                print(e, name)
        print(datetime.now())
        print(f'符合条件的stock num: {len(rs)}')
        return rs
