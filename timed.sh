#!/usr/bin/env bash
python timed_tasks.py
# 计算资产价格
python finance/cal_portfolio_val.py
# 爬取每日指标信息
python finance/stock_daily_basic2mongo.py


