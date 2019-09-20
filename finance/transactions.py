#!/usr/bin/python
# encoding: utf-8

"""
@author: Ian
@file: base.py
@time: 2019-09-16 16:51
"""
import sys
sys.path.append('/Users/luoyonggui/PycharmProjects/mayiutils_n1/mayiutils/db')
from pymongo_wrapper import PyMongoWrapper

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
    with open('data/transactions.txt') as f:
        ll = f.readlines()
    ll = [s.strip()[2:-2].split(', ') for s in ll]
    mongo = PyMongoWrapper()
    cols = 'trade_date account target price num fee_rate'.split()
    r = []
    for i in ll:
        # 买卖成本在买入时都算进去，卖出时不算成本
        t = [datetime.now(), i[3], i[0][:-1], float(i[2]), float(i[1]), 0.003]
        if t[2] == 'cash' or t[-2] < 0:  # 卖出时不算成本
            t[-1] = 0
        r.append(t)
        if t[2] != 'cash':
            # 每增加一笔feicash，就要加1笔-cash
            r.append([t[0], t[1], 'cash', 1, -t[3]*t[4]*(1+t[5]), 0])
    import pandas as pd
    df = pd.DataFrame(r, columns=cols)
    mongo.insertDataframe(df, 'finance', 'transactions')


if __name__ == '__main__':
    # add_transactions()
    transaction_list = []
    mongo = PyMongoWrapper()
    table = mongo.getCollection('finance', 'transactions')
    cols = 'trade_date account target price num fee_rate'.split()
    rs = mongo.findAll(table, fieldlist=cols, sort=[('trade_date', 1)])

    import pandas as pd
    df = pd.DataFrame(rs)
    df['trade_date'] = df['trade_date'].dt.date
    df.set_index('trade_date', inplace=True)
    df['cost'] = df['price'] * df['num'] * (1 + df.fee_rate)

    # 计算截止某日的账户切片
    df_ac = df.groupby(['account', 'target'])['num', 'cost'].sum()
    # 获取某一天的市值
    for line in df[['account', 'target']].drop_duplicates().itertuples():
        if line.account == 'cash':
            continue
        if line.account == 'PA':
            pass
        if line.account == 'ZLT':
            pass
        if line.account in ['TTA', 'TTJ']:
            pass


    print(df_ac)
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

