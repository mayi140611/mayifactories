#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: base.py
@time: 2019-09-16 16:51
"""
import os
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper

import pandas as pd
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 100)  # 设置显示数据的最大列数，防止出现省略号…，导致数据显示不全
pd.set_option('expand_frame_repr', False)  # 当列太多时不自动换行
import numpy as np


class Publisher:
    def __init__(self):
        pass

    def register(self):
        pass

    def unregister(self):
        pass

    def notify_all(self):
        pass


class Subscriber:
    def __init__(self):
        pass

    def notify(self):
        pass

from attr import attrs, attrib, fields
from cattr import unstructure, structure
from datetime import datetime, date


@attrs
class Transaction:
    num = attrib(type=float, default=0)
    price = attrib(type=float, default=0)
    fee_rate = attrib(type=float, default=0)
    trade_date = attrib(type=datetime, default=datetime.now())
    target = attrib(type=str, default='cash')
    account = attrib(type=str, default='pingan')


# @attrs
# class Position:
#     target = attrib(type=str)
#     num = attrib(type=float, default=0)
#     price_mean = attrib(type=float, default=0)

@attrs
class Trade(Publisher):
    _transaction_list = attrib(factory=list, repr=False)
    _accounts = attrib(factory=list)
    # def __init__(self, transaction_list):
    #     self._accounts = []
    #     self._transaction_list = transaction_list

    def register(self, account):
        if account not in self._accounts:
            self._accounts.append(account)

    def unregister(self, account):
        if account not in self._accounts:
            self._accounts.remove(account)

    def notify_all(self):
        for a in self._accounts:
            a.notify(self._transaction_list)


@attrs
class Account(Subscriber):
    _name = attrib(type=str)
    # _trade_list = attrib(type=list, default=[])
    # _trade_list = attrib(type=list, default=[])
    _trade_list = attrib(factory=list, repr=False)
    _positions = attrib(factory=dict)
    _cash = attrib(type=float, default=0)
    # def __init__(self, name):
    #     self._name = name
    #     self._trade_list = []
    #     self._positions = dict()  # target: (num, price_mean)
    #     self._cash = 0
    #
    # def __str__(self):
    #     return f'{self._name}: ' \
    #            f'{self._positions}\n{self._cash}'

    def notify(self, transaction_list):
        for t in transaction_list:
            if t.account == self._name:
                self._trade_list.append(t)
                if t.target == 'cash':
                    self._cash += t.num
                else:
                    num = t.num
                    amount = t.num * t.price
                    fee = 5 if amount*0.00025 < 5 else amount*0.00025
                    if t.target in self._positions:
                        num += self._positions[t.target][0]
                        amount += self._positions[t.target][1] * self._positions[t.target][0]
                    price_mean = (amount + fee)/num
                    self._positions[t.target] = (num, price_mean)
                # print(self)


def add_transactions():
    df = pd.read_excel('data/transactions.xlsx')
    r = []
    for line in df.itertuples():
        if line.target != 'cash':
            r.append([line.trade_date, line.account, 'cash', 1, -1 * (line.price * line.num * 1+line.fee_rate), 0])
    dft = pd.DataFrame(r, columns=df.columns)
    df = pd.concat([df, dft], ignore_index=True)
    # with open('data/transactions.txt') as f:
    #     ll = f.readlines()
    # ll = [s.strip()[2:-2].split(', ') for s in ll]
    # cols = 'trade_date account target price num fee_rate'.split()
    # r = []
    # for i in ll:
    #     # 买卖成本在买入时都算进去，卖出时不算成本
    #     t = [datetime.now(), i[3], i[0][:-1], float(i[2]), float(i[1]), 0.003]
    #     if t[2] == 'cash' or t[-2] < 0:  # 卖出时不算成本
    #         t[-1] = 0
    #     r.append(t)
    #     if t[2] != 'cash':
    #         # 每增加一笔not cash，就要加1笔-cash
    #         r.append([t[0], t[1], 'cash', 1, -t[3]*t[4]*(1+t[5]), 0])
    # df = pd.DataFrame(r, columns=cols)
    print(df)
    if not df.empty:
        mongo = PyMongoWrapper()
        mongo.insertDataframe(df, 'finance', 'transactions')
    else:
        print('no transactions!')

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
stock_series = pd.read_pickle(os.path.join(FILE_DIR, 'data/stock_dict.pkl'))
fund_otc_series = pd.read_pickle(os.path.join(FILE_DIR, 'data/fund_otc_series.pkl'))
series = stock_series.append(fund_otc_series)


def get_last_day_market_val(target, tdate):
    """
    获取最近一日市值
    :param target:
    :param tdate:
        '20190908'
    :return:
    """
    if target == 'cash':
        return datetime.now().date(), 1
    if any([target.endswith('.SZ'), target.endswith('.SH')]):
        tname = target
    else:
        tname = series.loc[target]
    mongo = PyMongoWrapper()
    db_name = 'finance_n'
    tb_name = 'stocks_daily'
    table = mongo.getCollection(db_name, tb_name)
    r = list(mongo.findAll(table, {'ts_code': tname, 'trade_date': {'$lte': datetime.strptime(tdate, '%Y%m%d')}}, fieldlist=['trade_date', 'close', 'pct_chg'], sort=[('trade_date', -1)], limit=1))[0]
    return r['trade_date'].date(), r['close']
    # rlist.append((i[0], r['close'], i[1], r['pct_chg'], g, r['trade_date']))


def get_account_val(trans_df, tdate):
    trans_df = trans_df[:tdate]
    # 计算截止某日的账户切片
    df_ac = trans_df.groupby(['account', 'target'])['num', 'cost'].sum()
    df_ac.reset_index(inplace=True)
    df_ac['price'] = 0
    df_ac['tdate'] = 0
    # 获取某一天的市值
    for i in trans_df['target'].unique():
        df_ac.loc[df_ac.target == i, ['tdate', 'price']] = get_last_day_market_val(i, tdate)
    df_ac['type'] = np.where((df_ac.account == 'PA') & (df_ac.target != 'cash'), 'STOCK',
                             np.where((df_ac.account == 'ZLT') & (df_ac.target != 'cash'), 'FUND',
                                      np.where((df_ac.account.isin(['TTJ', 'TTA'])) & (df_ac.target != 'cash'), 'OTC_FUND', 'cash')))
    # df_ac['type'] = 'cash'
    # df_ac.loc[(df_ac.account == 'PA') & (df_ac.target != 'cash'), 'type'] = 'STOCK'
    # df_ac.loc[(df_ac.account == 'ZLT') & (df_ac.target != 'cash'), 'type'] = 'FUND'
    # df_ac.loc[(df_ac.account.isin(['TTJ', 'TTA'])) & (df_ac.target != 'cash'), 'type'] = 'OTC_FUND'
    # print(df_ac)
    df_ac['market_val'] = df_ac.num * df_ac.price
    df_ac['profit'] = df_ac['market_val'] - df_ac['cost']
    print(df_ac)
    # print(df_ac)
    # print(df_ac.groupby(['account'])['market_val'].sum())
    # print(df_ac.groupby(['type'])['market_val'].sum())
    # print(f'profit: {df_ac.profit.sum()}')
    # s = df_ac.groupby(['type', 'target'])['market_val'].sum()
    s = df_ac.groupby('account')['market_val'].sum()
    # s = df_ac.groupby('type')['market_val'].sum()
    s.loc['TOTAL'] = s.sum()
    dfr = pd.DataFrame(s).T
    dfr.index.name = 'date'
    dfr.index = pd.to_datetime([tdate])
    return dfr


if __name__ == '__main__':
    # add_transactions()
    transaction_list = []
    mongo = PyMongoWrapper()
    table = mongo.getCollection('finance', 'transactions')
    cols = 'trade_date account target price num fee_rate'.split()
    rs = mongo.findAll(table, fieldlist=cols, sort=[('trade_date', 1)])

    trans_df = pd.DataFrame(rs)
    trans_df.set_index('trade_date', inplace=True)

    trans_df['cost'] = trans_df['price'] * trans_df['num'] * (1 + trans_df.fee_rate)
    dfc = pd.DataFrame()
    dates = pd.date_range('20190921', '20190926', freq='B')
    dfc = get_account_val(trans_df, '20190930')
    # for d in dates:
    #     d = d.strftime('%Y%m%d')
    #     if dfc.empty:
    #         dfc = get_account_val(trans_df, d)
    #     else:
    #         dfc = pd.concat([dfc, get_account_val(trans_df, d)])
    print(dfc)
    # dfc.plot(subplots=True, figsize=(8, 14))
    # import matplotlib.pyplot as plt
    #
    # plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.show()




    # trade = Trade(transaction_list)
    # ZLT = Account('ZLT')
    # PA = Account('PA')
    # TTA = Account('TTA')
    # TTJ = Account('TTJ')
    # trade.register(ZLT)
    # trade.register(PA)
    # trade.register(TTJ)
    # trade.register(TTA)
    # trade.notify_all()
    # print(trade)
    # print(unstructure(trade))

